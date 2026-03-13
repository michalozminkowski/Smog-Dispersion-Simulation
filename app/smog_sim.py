import os
import matplotlib
matplotlib.use('Agg')

is_docker = os.environ.get("DOCKER_ENV", "False") == "True"
if is_docker:
    matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patheffects as PathEffects
from app import config, map_utils, physics
from weather import WIND_DATA

def main():
    if getattr(config, 'STEPS_PER_DAY', 0) <= 0:
        config.STEPS_PER_DAY = 288

    # 1. POBIERANIE MAPY
    base_source, label_candidates, congestion_grid = map_utils.create_smog_map_with_congestion(
        "data/SREDNIE_KORKI.csv")

    # 2. SYMULACJA
    current_smog = np.zeros((config.GRID_SIZE, config.GRID_SIZE))
    recorded_frames = []
    max_pollution = 0
    total_steps = config.STEPS_PER_DAY * 2
    minutes_per_step = (24 * 60) / config.STEPS_PER_DAY

    for t in range(total_steps):
        day_name = 'Monday' if t < config.STEPS_PER_DAY else 'Tuesday'
        hour_idx = int((t * minutes_per_step) % (24 * 60) // 60) % 24

        if day_name == 'Monday':
            gios_pm10 = config.MONDAY_PROFILE[hour_idx]
        else:
            gios_pm10 = config.TUESDAY_PROFILE[hour_idx]

        current_congestion = congestion_grid[hour_idx, :, :] if congestion_grid is not None else np.ones(
            (config.GRID_SIZE, config.GRID_SIZE))

        forecast_idx = hour_idx // 3
        if forecast_idx >= len(WIND_DATA[day_name]): forecast_idx = len(WIND_DATA[day_name]) - 1
        wind_params = WIND_DATA[day_name][forecast_idx]

        current_traffic_volume = config.HOURLY_TRAFFIC[hour_idx]

        current_smog = physics.update_simulation_step(
            current_smog=current_smog,
            base_source=base_source,
            gios_pm10=gios_pm10,
            diffusion_rate=config.DIFFUSION_RATE,
            decay_rate=config.DECAY_RATE,
            wind_params=wind_params,
            congestion_map=current_congestion,
            traffic_volume=current_traffic_volume
        )

        if t >= config.STEPS_PER_DAY:
            recorded_frames.append(current_smog.copy())
            max_pollution = max(max_pollution, np.max(current_smog))

    if not recorded_frames:
        recorded_frames.append(current_smog.copy())
        max_pollution = np.max(current_smog) if np.max(current_smog) > 0 else 1.0

    fig, ax = plt.subplots(figsize=(9, 6))
    fig.subplots_adjust(left=0.38, right=0.95, top=0.88, bottom=0.1)

    im = ax.imshow(recorded_frames[0], cmap='inferno', vmin=0, vmax=max_pollution * 0.8, animated=True)
    ax.contour(base_source, levels=[0.5], colors='cyan', linewidths=0.4, alpha=0.3)

    for name, data in label_candidates.items():
        if data['length'] > 200:
            txt = ax.text(data['x'], data['y'], name, rotation=data['angle'], color='white', ha='center',
                          va='center', fontsize=7, alpha=0.5, rotation_mode='anchor')
            txt.set_path_effects([PathEffects.withStroke(linewidth=1, foreground='black', alpha=0.3)])

    plt.colorbar(im, fraction=0.046, pad=0.04).set_label('Symulowane Stężenie PM10 [µg/m³]')

    wind_arrow = None
    info_text = None

    def update(frame_idx):
        nonlocal wind_arrow, info_text

        im.set_data(recorded_frames[frame_idx])

        total_min = frame_idx * minutes_per_step
        hour, minute = int(total_min // 60) % 24, int(total_min % 60)

        forecast_idx = hour // 3
        if forecast_idx >= len(WIND_DATA['Tuesday']): forecast_idx = len(WIND_DATA['Tuesday']) - 1
        wind = WIND_DATA['Tuesday'][forecast_idx]
        wind_speed_kmh = wind['speed'] * 50
        dir_names = {(0, -1): 'N', (1, -1): 'NE', (1, 0): 'E', (1, 1): 'SE', (0, 1): 'S', (-1, 1): 'SW', (-1, 0): 'W',
                     (-1, -1): 'NW'}
        wind_dir = dir_names.get((wind['dir_x'], wind['dir_y']), '?')

        if congestion_grid is not None:
            hour_congestion = congestion_grid[hour, :, :]
            street_cells = hour_congestion[base_source > 0]
            if len(street_cells) > 0:
                avg_val = np.mean(street_cells)
                congestion_pct = int((avg_val - 1.0) * 100)
                if congestion_pct < 0: congestion_pct = 0
            else:
                congestion_pct = 0
        else:
            congestion_pct = 0

        if wind_arrow:
            wind_arrow.remove()

        start_x, start_y = 380, 50
        arrow_scale = 40

        wind_arrow = ax.annotate(
            '',
            xy=(start_x + wind['dir_x'] * arrow_scale, start_y + wind['dir_y'] * arrow_scale),
            xytext=(start_x, start_y),
            arrowprops=dict(
                arrowstyle='->,head_width=0.6,head_length=0.8',
                lw=3,
                color='deepskyblue'
            )
        )

        ax.text(start_x, start_y - 20, 'WIND', fontsize=9, color='deepskyblue',
                weight='bold', ha='center', va='center')

        bg_pm10 = config.TUESDAY_PROFILE[hour]

        info_lines = [
            "SMOG FORECAST",
            "Jeżyce, Poznań",
            "Tuesday, 03.02.2026",
            "─" * 25,
            f"Time: {hour:02d}:{minute:02d}",
            f"Avg. Congestion: +{congestion_pct}%",
            "─" * 25,
            f"Background (GIOS) (30%): {(bg_pm10 * 0.3):.1f} µg/m³",
            f"Traffic (70%): Congestion-dependent",
            "─" * 25,
            f"Wind: {wind_dir} ({wind_speed_kmh:.0f} km/h)",
            f"Max Concentration: {np.max(recorded_frames[frame_idx]):.1f} µg/m³"
        ]

        try:
            if info_text:
                info_text.remove()
        except Exception:
            pass

        info_text = ax.text(
            -0.08, 1.0, '\n'.join(info_lines),
            transform=ax.transAxes,
            fontsize=10, color='white',
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='#2c3e50', alpha=0.9, edgecolor='white')
        )

        ax.set_title("Smog Dispersion Simulation: 30% GIOS Background\n+ 70% (Congestion * Traffic)", fontsize=12,
                     fontweight='bold')

        return [im, wind_arrow, info_text]

    ani = animation.FuncAnimation(fig, update, frames=len(recorded_frames), interval=40, blit=False)
    ani.save('smog_symulacja.gif', writer='pillow', fps=10, dpi=80)

    plt.close('all')

if __name__ == "__main__":
    main()