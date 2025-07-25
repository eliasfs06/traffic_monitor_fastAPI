import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import TrafficRaw, TrafficStatus, DeviceHealth
from collections import defaultdict, Counter

# Configuração do banco
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/traffic-monitor"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def format_street_name(street_id: str) -> str:
    return street_id.replace("_", " ").title()

def plot_vehicle_count():
    print("Plotando gráfico de veículos...")
    results = session.query(TrafficRaw).order_by(TrafficRaw.timestamp).all()

    if not results:
        print("Nenhum dado em traffic_raw.")
        return

    timestamps = [r.timestamp for r in results]
    counts = [r.vehicle_count for r in results]

    plt.figure(figsize=(10, 4))
    plt.plot(timestamps, counts, marker='o')
    plt.title("Contagem de veículos ao longo do tempo")
    plt.xlabel("Horário")
    plt.ylabel("Qtde de veículos")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.gcf().autofmt_xdate()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("vehicle_count.png")
    plt.close()

def plot_congestion_levels():
    print("Plotando gráfico de congestionamento...")
    results = session.query(TrafficStatus).all()

    if not results:
        print("Nenhum dado em traffic_status.")
        return

    levels = [r.congestion_level for r in results]
    counts = Counter(levels)

    colors = {"low": "green", "medium": "orange", "high": "red"}

    plt.figure(figsize=(6, 4))
    plt.bar(counts.keys(), counts.values(), color=[colors.get(k, "gray") for k in counts.keys()])
    plt.title("Frequência dos níveis de congestionamento")
    plt.xlabel("Nível")
    plt.ylabel("Ocorrências")
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig("congestion_levels.png")
    plt.close()

def plot_vehicle_avg_by_street():
    print("Plotando média de veículos por rua...")
    results = session.query(TrafficRaw).all()

    if not results:
        print("Nenhum dado em traffic_raw.")
        return

    street_data = defaultdict(list)
    for r in results:
        street = format_street_name(r.street_id)
        street_data[street].append(r.vehicle_count)

    avg_counts = {k: sum(v) / len(v) for k, v in street_data.items()}

    plt.figure(figsize=(8, 4))
    plt.bar(avg_counts.keys(), avg_counts.values(), color="blue")
    plt.title("Média de veículos por rua")
    plt.xlabel("Rua")
    plt.ylabel("Média de veículos")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("avg_vehicles_by_street.png")
    plt.close()

def plot_congestion_by_street():
    print("Plotando níveis de congestionamento por rua...")
    results = session.query(TrafficStatus).all()

    if not results:
        print("Nenhum dado em traffic_status.")
        return

    street_levels = defaultdict(list)
    for r in results:
        street = format_street_name(r.street_id)
        street_levels[street].append(r.congestion_level)

    streets = sorted(street_levels.keys())
    levels = ["low", "medium", "high"]
    level_colors = {"low": "green", "medium": "orange", "high": "red"}

    counts_per_level = {level: [] for level in levels}
    for street in streets:
        counter = Counter(street_levels[street])
        for level in levels:
            counts_per_level[level].append(counter.get(level, 0))

    x = np.arange(len(streets))
    width = 0.25

    plt.figure(figsize=(10, 6))
    for idx, level in enumerate(levels):
        plt.bar(
            x + idx * width,
            counts_per_level[level],
            width=width,
            label=level.capitalize(),
            color=level_colors[level]
        )

    plt.title("Distribuição dos níveis de congestionamento por rua")
    plt.xlabel("Rua")
    plt.ylabel("Ocorrências")
    plt.xticks(x + width, streets, rotation=45)
    plt.legend(title="Nível")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("congestion_by_street.png")
    plt.close()

def plot_congestion_comparison_by_hour():
    print("Gerando gráficos comparativos por hora e rua...")
    results = session.query(TrafficStatus).all()

    if not results:
        print("Nenhum dado em traffic_status.")
        return

    data = [{
        "timestamp": r.timestamp.replace(minute=0, second=0, microsecond=0),
        "street": format_street_name(r.street_id),
        "level": r.congestion_level
    } for r in results]

    df = pd.DataFrame(data)
    grouped = df.groupby(["timestamp", "street", "level"]).size().unstack(fill_value=0).reset_index()

    for street in grouped["street"].unique():
        df_street = grouped[grouped["street"] == street].set_index("timestamp")
        levels_present = [lvl for lvl in ["low", "medium", "high"] if lvl in df_street.columns]
        df_street = df_street[levels_present]

        df_street.plot(
            kind="bar",
            stacked=True,
            figsize=(10, 5),
            color={"low": "green", "medium": "orange", "high": "red"}
        )
        plt.title(f"Comparativo de status de tráfego por hora - {street}")
        plt.xlabel("Hora")
        plt.ylabel("Ocorrências")
        plt.xticks(rotation=45)
        plt.legend(title="Nível")
        plt.tight_layout()
        filename = f"congestion_by_hour_{street.replace(' ', '_').lower()}.png"
        plt.savefig(filename)
        plt.close()

if __name__ == "__main__":
    plot_vehicle_count()
    plot_congestion_levels()
    plot_vehicle_avg_by_street()
    plot_congestion_by_street()
    plot_congestion_comparison_by_hour()