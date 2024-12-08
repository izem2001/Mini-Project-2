import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MedalAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Paris 2024 Medal Analysis")
        self.root.geometry("850x650")

        self.create_widgets()
        self.medal_data = None

    def create_widgets(self):
        # URL input for medal data scraping
        tk.Label(self.root, text="Enter the URL for Medal Data:").pack(pady=5)

        self.url_entry = tk.Entry(self.root, width=75)
        self.url_entry.pack(pady=5)
        self.url_entry.insert(0, "https://www.bbc.com/sport/olympics/paris-2024/medals")

        tk.Button(self.root, text="Fetch Data", command=self.fetch_medal_data).pack(pady=5)

        # Listbox for displaying countries
        self.country_listbox = tk.Listbox(self.root, width=55, height=12)
        self.country_listbox.pack(pady=15)

        # Buttons for data visualization
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)

        tk.Button(button_frame, text="Country Medal Chart", command=self.display_country_medal_chart).pack(side=tk.LEFT, padx=8)
        tk.Button(button_frame, text="Top Country Analytics", command=self.display_analytics).pack(side=tk.LEFT, padx=8)

    def fetch_medal_data(self):
        """Fetch medal data from the given URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            url = self.url_entry.get()
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            countries = []
            gold = []
            silver = []
            bronze = []

            table_rows = soup.find_all('tr')[1:]  # Skipping the header row
            for row in table_rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    countries.append(cols[1].text.strip())
                    gold.append(int(cols[2].text.strip() or 0))
                    silver.append(int(cols[3].text.strip() or 0))
                    bronze.append(int(cols[4].text.strip() or 0))

            self.medal_data = pd.DataFrame({
                'Country': countries,
                'Gold': gold,
                'Silver': silver,
                'Bronze': bronze
            })

            self.medal_data['Total'] = self.medal_data['Gold'] + self.medal_data['Silver'] + self.medal_data['Bronze']

            self.update_country_listbox()

            messagebox.showinfo("Data Loaded", f"Successfully loaded data for {len(self.medal_data)} countries.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load medal data: {str(e)}")

    def update_country_listbox(self):
        """Update the listbox with country names"""
        self.country_listbox.delete(0, tk.END)
        for country in self.medal_data['Country']:
            self.country_listbox.insert(tk.END, country)

    def display_country_medal_chart(self):
        """Display a bar chart for selected country's medals"""
        if self.medal_data is None:
            messagebox.showerror("Error", "Please load data first.")
            return

        selected_indices = self.country_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select a country.")
            return

        country = self.country_listbox.get(selected_indices[0])
        country_info = self.medal_data[self.medal_data['Country'] == country]

        plt.figure(figsize=(8, 5))
        medal_types = ['Gold', 'Silver', 'Bronze']
        medal_values = [
            country_info['Gold'].values[0],
            country_info['Silver'].values[0],
            country_info['Bronze'].values[0]
        ]

        plt.bar(medal_types, medal_values, color=['gold', 'silver', 'brown'])
        plt.title(f"{country} Medal Counts")
        plt.ylabel('Medals')

        chart_window = tk.Toplevel(self.root)
        chart_window.title(f"{country} Medal Distribution")

        canvas = FigureCanvasTkAgg(plt.gcf(), master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def display_analytics(self):
        """Display analytics using pie and line charts"""
        if self.medal_data is None:
            messagebox.showerror("Error", "Please load data first.")
            return

        top_countries = self.medal_data.nlargest(10, 'Total')

        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("Top Country Medal Analytics")
        analytics_window.geometry("1300x900")

        fig, axs = plt.subplots(2, 2, figsize=(16, 12))

        axs[0, 0].pie(top_countries['Gold'], labels=top_countries['Country'], autopct='%1.1f%%', colors=['gold'])
        axs[0, 0].set_title('Gold Medals (Top 10)')

        axs[0, 1].pie(top_countries['Silver'], labels=top_countries['Country'], autopct='%1.1f%%', colors=['silver'])
        axs[0, 1].set_title('Silver Medals (Top 10)')

        axs[1, 0].pie(top_countries['Bronze'], labels=top_countries['Country'], autopct='%1.1f%%', colors=['brown'])
        axs[1, 0].set_title('Bronze Medals (Top 10)')

        axs[1, 1].plot(top_countries['Country'], top_countries['Total'], marker='o')
        axs[1, 1].set_title('Total Medal Count of Top 10 Countries')
        axs[1, 1].set_xlabel('Countries')
        axs[1, 1].set_ylabel('Total Medals')
        axs[1, 1].tick_params(axis='x', rotation=45)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=analytics_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def run_app():
    root = tk.Tk()
    app = MedalAnalysisApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()


# References:
# 1. https://github.com/Kanangnut/Paris-Olympic-2024-Dashboard-Analysis/blob/main/PythonScript/Python_Script.ipynb
# 2. https://www.kaggle.com/code/ibrahimhabibeg/2024-olympic-medalists-a-nation-level-analysis
# 3. ChatGPT (OpenAI) - Used for assistance in code generation and problem-solving
