from pathlib import Path

from metadata import load_frequency_data


project_folder = Path(__file__).parent
frequency_file = project_folder / "data" / "cuhk_taiwan_frequency.txt"

frequency_data = load_frequency_data(frequency_file)

print(f"Characters loaded: {len(frequency_data)}")

print("\n的:")
print(frequency_data["的"])

print("\n愛:")
print(frequency_data["愛"])
