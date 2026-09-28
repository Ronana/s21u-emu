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
# FPS is derived from SurfaceFlinger's composited-frame counter (service call 1013),
# i.e. frames actually presented to the display. Cross-check with the emulator's
# own FPS overlay.

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

# Uptime in centiseconds (integer maths only; mksh has no floats).
uptime_cs() {
    read -r up _ < /proc/uptime
    echo "${up%.*}${up#*.}"
}

rd() { cat "$1" 2>/dev/null || echo ""; }
mhz() { v=$(rd "$1"); [ -n "$v" ] && echo $((v / 1000)); }   # kHz -> MHz (CPU and GPU both report kHz)
milli_c() { v=$(rd "$1"); [ -n "$v" ] && echo $((v / 1000)); }  # m°C -> °C

echo "t_s,fps,cpu_little_mhz,cpu_mid_mhz,cpu_big_mhz,gpu_mhz,gpu_busy_pct,temp_big_c,temp_mid_c,temp_little_c,temp_gpu_c,temp_batt_c,batt_pct,batt_current_ma,charging" > "$OUT"
echo "perflog: logging ${DURATION}s every ${INTERVAL}s -> $OUT"

start=$(uptime_cs)
prev_t=$start
prev_f=$(sf_frames)
end=$((start + DURATION * 100))

while :; do
    sleep "$INTERVAL"
    now=$(uptime_cs)
    frames=$(sf_frames)

    dt=$((now - prev_t))
    df=$((frames - prev_f))
    [ "$dt" -gt 0 ] || dt=1
    fps10=$((df * 1000 / dt))           # FPS x10 for one decimal place
    fps="$((fps10 / 10)).$((fps10 % 10))"
    prev_t=$now
    prev_f=$frames

    t=$(((now - start) / 100))
    batt_t=$(rd $BATT/temp)             # tenths of °C
    busy=$(rd $GPU/gpu_busy); busy=${busy%%%}; busy=$(echo $busy)   # strip "%" and padding

    echo "$t,$fps,$(mhz $CPUFREQ/policy0/scaling_cur_freq),$(mhz $CPUFREQ/policy4/scaling_cur_freq),$(mhz $CPUFREQ/policy7/scaling_cur_freq),$(mhz $GPU/gpu_clock),$busy,$(milli_c "$T_BIG"),$(milli_c "$T_MID"),$(milli_c "$T_LITTLE"),$(milli_c "$T_GPU"),$((batt_t / 10)).$((batt_t % 10)),$(rd $BATT/capacity),$(rd $BATT/current_now),$(rd $BATT/status)" >> "$OUT"

    [ "$now" -ge "$end" ] && break
done

echo "perflog: done ($t s) -> $OUT"
