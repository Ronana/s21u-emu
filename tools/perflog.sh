#!/system/bin/sh
# perflog.sh: on-device performance/thermal logger for the Galaxy S21 Ultra (Exynos 2100).
#
# Samples FPS, CPU/GPU clocks, GPU load and temperatures at a fixed interval and
# writes a CSV, so emulator runs can be compared before/after tuning.
#
# Usage (as root on the device):
#   su -c sh /data/local/tmp/perflog.sh [duration_s] [interval_s] [output.csv]
# Defaults: 900 s (15 min), 2 s interval, /sdcard/perflog/perflog-<epoch>.csv
#
# Two frame rates are logged:
#   game_fps    - frames queued by the app's own game surface (SurfaceView), from
#                 SurfaceFlinger timestats. This is the emulator's real output rate.
#   display_fps - how often SurfaceFlinger composited the whole screen (service call
#                 1013). This can run at the 120 Hz panel rate even when the game
#                 produces 60, e.g. Dolphin, so don't use it as game FPS.
# Cross-check game_fps with the emulator's own FPS overlay.

DURATION=${1:-900}
INTERVAL=${2:-2}
OUT=${3:-/sdcard/perflog/perflog-$(date +%s).csv}

GPU=/sys/kernel/gpu
CPUFREQ=/sys/devices/system/cpu/cpufreq
BATT=/sys/class/power_supply/battery

if [ "$(id -u)" != "0" ]; then
    echo "perflog: must run as root (su -c sh $0 ...)" >&2
    exit 1
fi

mkdir -p "$(dirname "$OUT")" || exit 1

# Map thermal zone type -> sysfs path once, so column order is stable.
zone_path() {
    for z in /sys/class/thermal/thermal_zone*; do
        [ "$(cat "$z/type" 2>/dev/null)" = "$1" ] && { echo "$z/temp"; return; }
    done
}
T_BIG=$(zone_path BIG)
T_MID=$(zone_path MID)
T_LITTLE=$(zone_path LITTLE)
T_GPU=$(zone_path G3D)

# Frames composited so far, decoded from "Result: Parcel(<tab>00001e92    '....')".
sf_frames() {
    hex=$(service call SurfaceFlinger 1013 | sed -n 's/.*Parcel([[:space:]]*\([0-9a-f]*\).*/\1/p')
    echo $((16#${hex:-0}))
}

# Cumulative frames of the busiest game surface: "<totalFrames> <layer name>".
# (Count first, space-separated: mksh treats "|" specially in ${var%pattern}.)
# Timestats is enabled at start and read cumulatively (no clearing) so no frames
# are lost between samples.
game_layer_frames() {
    dumpsys SurfaceFlinger --timestats -dump 2>/dev/null | awk '
        /^layerName = / { name = substr($0, 13) }
        /^totalFrames = / && name ~ /SurfaceView/ {
            if ($3 + 0 > best) { best = $3 + 0; bestname = name }
            name = ""
        }
        END { print best + 0 " " bestname }'
}

# Uptime in centiseconds (integer maths only; mksh has no floats).
uptime_cs() {
    read -r up _ < /proc/uptime
    echo "${up%.*}${up#*.}"
}

rd() { cat "$1" 2>/dev/null || echo ""; }
mhz() { v=$(rd "$1"); [ -n "$v" ] && echo $((v / 1000)); }   # kHz -> MHz (CPU and GPU both report kHz)
milli_c() { v=$(rd "$1"); [ -n "$v" ] && echo $((v / 1000)); }  # m°C -> °C

echo "t_s,game_fps,display_fps,cpu_little_mhz,cpu_mid_mhz,cpu_big_mhz,gpu_mhz,gpu_busy_pct,temp_big_c,temp_mid_c,temp_little_c,temp_gpu_c,temp_batt_c,batt_pct,batt_current_ma,charging" > "$OUT"
echo "perflog: logging ${DURATION}s every ${INTERVAL}s -> $OUT"

dumpsys SurfaceFlinger --timestats -clear -enable >/dev/null 2>&1
trap 'dumpsys SurfaceFlinger --timestats -disable >/dev/null 2>&1' EXIT INT TERM

start=$(uptime_cs)
prev_t=$start
prev_f=$(sf_frames)
prev_g=$(game_layer_frames)
end=$((start + DURATION * 100))

while :; do
    sleep "$INTERVAL"
    now=$(uptime_cs)
    frames=$(sf_frames)
    game=$(game_layer_frames)

    dt=$((now - prev_t))
    df=$((frames - prev_f))
    [ "$dt" -gt 0 ] || dt=1
    fps10=$((df * 1000 / dt))           # FPS x10 for one decimal place
    fps="$((fps10 / 10)).$((fps10 % 10))"
    # Game FPS: only diff the same layer; a new layer (game restarted) resets the count.
    if [ "${game#* }" = "${prev_g#* }" ] && [ -n "${game#* }" ]; then
        dg=$((${game%% *} - ${prev_g%% *}))
    else
        dg=0
    fi
    gfps10=$((dg * 1000 / dt))
    gfps="$((gfps10 / 10)).$((gfps10 % 10))"

    prev_t=$now
    prev_f=$frames
    prev_g=$game

    t=$(((now - start) / 100))
    batt_t=$(rd $BATT/temp)             # tenths of °C
    busy=$(rd $GPU/gpu_busy); busy=${busy%%%}; busy=$(echo $busy)   # strip "%" and padding

    echo "$t,$gfps,$fps,$(mhz $CPUFREQ/policy0/scaling_cur_freq),$(mhz $CPUFREQ/policy4/scaling_cur_freq),$(mhz $CPUFREQ/policy7/scaling_cur_freq),$(mhz $GPU/gpu_clock),$busy,$(milli_c "$T_BIG"),$(milli_c "$T_MID"),$(milli_c "$T_LITTLE"),$(milli_c "$T_GPU"),$((batt_t / 10)).$((batt_t % 10)),$(rd $BATT/capacity),$(rd $BATT/current_now),$(rd $BATT/status)" >> "$OUT"

    [ "$now" -ge "$end" ] && break
done

echo "perflog: done ($t s) -> $OUT"
