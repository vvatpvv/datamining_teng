import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

df = pd.read_csv("device_attributes_filtered_verif.csv")

def convert_voltage(value):
    if pd.isna(value):
        return None
    s = str(value).strip().lower()
    num = ''.join([c for c in s if (c.isdigit() or c in ['.', '-', 'e'])])
    try:
        val = float(num)
    except:
        return None

    if 'kv' in s:
        return val * 1000
    elif 'mv' in s:
        return val / 1000
    elif 'µv' in s or 'uv' in s:
        return val / 1_000_000
    elif 'v' in s:
        return val
    else:
        return val

def convert_current(value):
    if pd.isna(value):
        return None
    s = str(value).strip().lower()
    num = ''.join([c for c in s if (c.isdigit() or c in ['.', '-', 'e'])])
    try:
        val = float(num)
    except:
        return None

    if 'ka' in s:
        return val * 1000
    elif 'ma' in s:
        return val / 1000
    elif 'µa' in s or 'ua' in s:
        return val / 1_000_000
    elif 'na' in s:  # nanoampere
        return val / 1_000_000_000
    elif 'pa' in s:  # picoampere
        return val / 1_000_000_000_000
    elif 'fa' in s:  # femtoampere
        return val / 1_000_000_000_000_000
    elif 'a' in s:
        if 'μ' in value:
            return val / 1_000_000
        return val
    else:
        return val

def convert_power_density(value, target_unit="W/m2"):
    """ target_unit: "W/m2" or "W/cm2" or "mW/m2"
    """
    if pd.isna(value):
        return None
    s = str(value).strip().lower()

    num = ''.join([c for c in s if (c.isdigit() or c in ['.', '-', 'e'])])
    try:
        val = float(num)
    except:
        return None

    if re.search(r'kw\s*/?\s*m', s) or 'kw m-2' in s or 'kw m⁻²' in s:
        val = val * 1000
    elif re.search(r'mw\s*/?\s*m', s) or 'mw m-2' in s or 'mw m⁻²' in s:
        val = val / 1000
    elif re.search(r'(µw|uw)\s*/?\s*m', s) or 'µw m-2' in s or 'uw m⁻²' in s:
        val = val / 1_000_000
    elif re.search(r'w\s*/?\s*m', s) or 'w m-2' in s or 'w m⁻²' in s:
        val = val
    elif re.search(r'kw\s*/?\s*cm', s) or 'kw cm-2' in s or 'kw cm⁻²' in s:
        val = (val * 1000) * 10000   # convert to W/m²
    elif re.search(r'mw\s*/?\s*cm', s) or 'mw cm-2' in s or 'mw cm⁻²' in s:
        val = (val / 1000) * 10000
    elif re.search(r'(µw|uw)\s*/?\s*cm', s) or 'µw cm-2' in s or 'uw cm⁻²' in s:
        val = (val / 1_000_000) * 10000
    elif re.search(r'w\s*/?\s*cm', s) or 'w cm-2' in s or 'w cm⁻²' in s:
        val = val * 10000
    else:
        if 'mW·m−2' in value:
            val = val * 1000
        elif 'mW·cm−2' in value:
            val = (val / 1000) * 10000
        elif 'W·cm−2' in value:
            val = val * 10000
        else:
            val = val

    # Convert to target unit
    if target_unit.lower() in ["w/cm2", "w/cm²", "w cm-2", "w cm⁻²"]:
        return val / 10000
    elif target_unit.lower() in ["mw/m2", "mw/m²", "mw m-2", "mw m⁻²"]:
        return val * 1000
    else:
        return val

def convert_current_density(value, target_unit="A/cm2"):
    """target_unit: "A/cm2" or "A/m2"
    """
    if pd.isna(value):
        return None
    s = str(value).strip().lower()
    num = ''.join([c for c in s if (c.isdigit() or c in ['.', '-', 'e'])])
    try:
        val = float(num)
    except:
        return None

    if re.search(r'ka\s*/?\s*cm', s) or 'ka cm-2' in s or 'ka cm⁻²' in s:
        val = val * 1000
    elif re.search(r'ma\s*/?\s*cm', s) or 'ma cm-2' in s or 'ma cm⁻²' in s:
        val = val / 1000
    elif re.search(r'(µa|ua)\s*/?\s*cm', s) or 'µa cm-2' in s or 'ua cm⁻²' in s:
        val = val / 1_000_000
    elif re.search(r'a\s*/?\s*cm', s) or 'a cm-2' in s or 'a cm⁻²' in s:
        val = val
    elif re.search(r'ka\s*/?\s*m', s) or 'ka m-2' in s or 'ka m⁻²' in s:
        val = (val * 1000) / 10000
    elif re.search(r'ma\s*/?\s*m', s) or 'ma m-2' in s or 'ma m⁻²' in s:
        val = (val / 1000) / 10000
    elif re.search(r'(µa|ua)\s*/?\s*m', s) or 'µa m-2' in s or 'ua m⁻²' in s:
        val = (val / 1_000_000) / 10000
    elif re.search(r'a\s*/?\s*m', s) or 'a m-2' in s or 'a m⁻²' in s:
        val = val / 10000
    else:
        val = val

    if target_unit.lower() in ["a/m2", "a/m²", "a m-2", "a m⁻²"]:
        return val * 10000
    else:
        return val  # default A/cm²

# unit conversion and descriptive statistics
df['Open_circuit_voltage_num'] = df['Open_circuit_voltage'].apply(convert_voltage)
print(df['Open_circuit_voltage_num'].describe())
df['Short_circuit_current_num'] = df['Short_circuit_current'].apply(convert_current)
print(df['Short_circuit_current_num'].describe())
df['Power_density_num'] = df['Power_density'].apply(lambda x: convert_power_density(x, target_unit="mW/m2"))
print(df['Power_density_num'].describe())
df['Current_density_num'] = df['Current_density'].apply(lambda x: convert_current_density(x, target_unit="A/cm2"))
print(df['Current_density_num'].describe())

def remove_outliers(series, threshold=0.1):
    z_scores = (series - series.mean()) / series.std()
    return series[(abs(z_scores) < threshold)]

voc = remove_outliers(df['Open_circuit_voltage_num'].dropna())
isc = remove_outliers(df['Short_circuit_current_num'].dropna())
p_d = remove_outliers(df['Power_density_num'].dropna(), 0.3)
jsc = remove_outliers(df['Current_density_num'].dropna(), 0.25)
print(voc.describe())
print(isc.describe())
print(p_d.describe())
print(jsc.describe())

fig, axes = plt.subplots(2, 1, figsize=(8,6), gridspec_kw={'height_ratios':[3,1]})
# Histogram
sns.histplot(voc, bins=50, color='lightgreen', edgecolor='black', ax=axes[0])
axes[0].set_yscale('log')
axes[0].set_xlabel("")
axes[0].set_ylabel("Count (log scale)")
axes[0].set_title("Distribution of Open Circuit Voltage")
# Boxplot
sns.boxplot(x=voc, color='lightgreen', ax=axes[1])
axes[1].set_xlabel("Open Circuit Voltage (V)")
# axes[1].set_title("Boxplot of Open Circuit Voltage")
plt.tight_layout()
plt.show()

# keep only values between 0 and 0.0004 A
isc_range = isc[(isc >= 0) & (isc <= 0.0004)]
print(isc_range.describe())

fig, axes = plt.subplots(2, 1, figsize=(8,6), gridspec_kw={'height_ratios':[3,1]})
# Histogram for Isc below 0.0004 A
sns.histplot(isc_range, bins=50, color='salmon', edgecolor='black', ax=axes[0])
axes[0].set_yscale('log')
axes[0].set_xlabel("")
axes[0].set_ylabel("Count (log scale)")
axes[0].set_title("Distribution of Short Circuit Current (≤0.0004 A)")
# Boxplot for Isc below 0.0004 A
sns.boxplot(x=isc_range, color='salmon', ax=axes[1])
axes[1].set_xlabel("Short Circuit Current (A)")
axes[1].set_title("")
plt.tight_layout()
plt.show()

# keep only values between 0 and 5000 mW/m²
p_d_range = p_d[(p_d >= 0) & (p_d <= 5000)]
print(p_d_range.describe())

fig, axes = plt.subplots(2, 1, figsize=(8,6), gridspec_kw={'height_ratios':[3,1]})
# Histogram for PD in mW/m²
sns.histplot(p_d_range, bins=50, color='orchid', edgecolor='black', ax=axes[0])
axes[0].set_yscale('log')
axes[0].set_xlabel("")
axes[0].set_ylabel("Count (log scale)")
axes[0].set_title("Distribution of Power Density (≤5000 mW/m²)")
axes[0].set_yticks([])
# Boxplot for PD
sns.boxplot(x=p_d_range, color='orchid', ax=axes[1])
axes[1].set_xlabel("Power Density (mW/m²)")
axes[1].set_title("")
plt.tight_layout()
plt.show()

# keep only values between 0 and 2
jsc_range = jsc[(jsc >= 0) & (jsc <= 0.0002)]
print(jsc_range.describe())

fig, axes = plt.subplots(2, 1, figsize=(8,6), gridspec_kw={'height_ratios':[3,1]})
# Histogram for Jsc with log scale
sns.histplot(jsc_range, bins=50, color='cyan', edgecolor='black', ax=axes[0])
axes[0].set_yscale('log')
axes[0].set_xlabel("")
axes[0].set_ylabel("Count (log scale)")
axes[0].set_title("Distribution of Current Density (Jsc)")
axes[0].set_yticks([])
# Boxplot for Jsc
sns.boxplot(x=jsc_range, color='cyan', ax=axes[1])
axes[1].set_xlabel("Current Density (A/cm²)")
axes[1].set_title("")
plt.tight_layout()
plt.show()


# Convert Date column from string to datetime
df['Ref_publication_date'] = pd.to_datetime(df['Ref_publication_date'], errors='coerce', infer_datetime_format=True)

# Drop rows with invalid/missing dates or voltages
plot_df = df.dropna(subset=['Ref_publication_date', 'Open_circuit_voltage_num'])
plot_df = plot_df.sort_values('Ref_publication_date')

# Scatter plot
plt.figure(figsize=(10,6))
plt.scatter(plot_df['Ref_publication_date'], plot_df['Open_circuit_voltage_num'], alpha=0.7)
plt.xlabel('Publication Date')
plt.ylabel('Open Circuit Voltage (V)')
plt.title('Open Circuit Voltage vs Publication Date')
plt.ylim(0, 1000)
plt.grid(True)
plt.tight_layout()
plt.show()

# Drop rows with invalid/missing dates or power density values
plot_df = df.dropna(subset=['Ref_publication_date', 'Power_density_num'])
plot_df = plot_df.sort_values('Ref_publication_date')

# Scatter plot
plt.figure(figsize=(10,6))
plt.scatter(plot_df['Ref_publication_date'], plot_df['Power_density_num'], alpha=0.7)
plt.xlabel('Publication Date')
plt.ylabel('Power Density (mW/m²)')
plt.title('Power Density vs Publication Date')
plt.ylim(0, 10000)
plt.grid(True)
plt.tight_layout()
plt.show()


# Count (mode)
mode_counts = df['Mode'].value_counts()
print(mode_counts)

# Bar chart for count (mode)
plt.figure(figsize=(6,4))
mode_counts.plot(kind='bar', color=['skyblue','salmon','lightgreen','orange'], edgecolor='black')
plt.xlabel("TENG Mode")
plt.ylabel("Count")
plt.title("Occurrences of Modes")
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()

# Count (materials)
pos_counts = df['Tribopositive'].value_counts().head(5)
print(pos_counts)
neg_counts = df['Tribonegative'].value_counts().head(5)
print(neg_counts)
ele_counts = df['Electrode'].value_counts().head(5)
print(ele_counts)

