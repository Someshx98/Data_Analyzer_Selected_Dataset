import pandas as pd
import base64 as bs
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Environment, FileSystemLoader

# --- ADDED: Turn off scientific (e+) notation globally ---
pd.set_option('display.float_format', '{:.2f}'.format)

file = pd.read_csv(r"D:\AIML Projects\Phase 2\Minor 1\data.csv")

total_null = file.isnull().sum()
print(total_null)

total_rows = len(file)
print(total_rows)

percentage_null = (total_null / total_rows) * 100
print(percentage_null)

total_duplicates = file.duplicated().sum()
print(total_duplicates)

file.columns = file.columns.str.replace('\xa0', ' ', regex = False).str.strip()
print(file.columns.tolist())

file["Actual gross"] = (
   file["Actual gross"]
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.split('[').str[0]
    .astype(float)
    .astype(int)
)

file["Adjusted gross (in 2022 dollars)"] = (
   file["Adjusted gross (in 2022 dollars)"]
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.split('[').str[0]
    .astype(float)
    .astype(int)
)

file["Average gross"] = (
   file["Average gross"]
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.split('[').str[0]
    .astype(float)
    .astype(int)
)

file_datatypes = file.dtypes
print(file_datatypes)

file_uniqueness = file.nunique()
print(file_uniqueness)

file_stats = file.describe()
print(file_stats)

numerics = file.select_dtypes(include = "number")
print(numerics)

Q1 = numerics.quantile(0.25)
Q3 = numerics.quantile(0.75)
IQR = Q3 - Q1
print(IQR)

lower_value = Q1 - 1.5 * IQR
upper_value = Q3 + 1.5 * IQR
print(lower_value, upper_value)

outlier_count = ((numerics < lower_value) | (numerics > upper_value)).sum()
print(outlier_count)

corr_matrix = numerics.corr()
print(corr_matrix)

plt.figure(figsize = (20, 16))
sns.heatmap(corr_matrix, annot=True, cmap = "YlGnBu")
plt.savefig("corr_matrix_heatmap.png", bbox_inches = "tight")
plt.close()

plt.figure(figsize = (25, 12))
sns.heatmap(file.isnull(), cbar = False, cmap = "YlGnBu")
plt.xticks(rotation=45)
plt.savefig("isnull_heatmap.png", bbox_inches = "tight")
plt.close()

# --- FIXED: Only loop through numeric columns so seaborn doesn't crash on text ---
for column in numerics.columns:
    plt.figure(figsize = (20, 12))
    sns.histplot(file[column], kde = True)
    plt.xticks(rotation=90)
    plt.savefig(f"hist_{column}.png", bbox_inches = "tight")
    plt.close()

# --- ADDED: float_format to force normal numbers in the HTML table ---
html_stats = file_stats.to_html(float_format='{:.2f}'.format)
html_missing = pd.DataFrame({"Missing" : total_null, "Percentage" : percentage_null}).to_html()

def image_to_base64(file_path):
    """Reads a local image file and converts it to a Base64 string."""
    try:
        with open(file_path, "rb") as image_file:
            data = image_file.read()
            encoded = bs.b64encode(data)
            return encoded.decode('utf-8')
    except FileNotFoundError:
        return ""

missing_base64 = image_to_base64("isnull_heatmap.png")
correlation_base64 = image_to_base64("corr_matrix_heatmap.png")

dist_plots_html = ""

for column in numerics.columns:
    file_name = f"hist_{column}.png"
    encoded_string = image_to_base64(file_name)

    if encoded_string:
        dist_plots_html += f'<div><h4>{column} Distribution</h4><img src="data:image/png;base64,{encoded_string}" alt="{column}"></div>\n'

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('report.html')

html_out = template.render(
    total_rows=total_rows,
    total_columns=len(file.columns),
    total_duplicates=total_duplicates,
    missing_values_table=html_missing,
    basic_stats_table=html_stats,
    missing_heatmap_img=missing_base64,
    correlation_img=correlation_base64,
    distribution_plots=dist_plots_html
)

with open("final_report.html", "w", encoding="utf-8") as output_file:
    output_file.write(html_out)

print("SUCCESS: final_report.html has been generated!")