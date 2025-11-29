import pandas as pd
from datetime import datetime, timedelta
from plotnine import ggplot, aes, geom_line, geom_point, geom_hline, labs, theme_bw, theme, element_text, scale_color_manual
import matplotlib.pyplot as plt
# read csv

df = pd.read_csv("storage/apartments.csv",
                 parse_dates=["ConsultationDate", "Moving in"])

df["CreditDays"] = pd.to_numeric(df["CreditDays"], errors="coerce")

# take only 7 days back

seven_days_ago = datetime.now() - timedelta(days=7)
df['Title'] = df['Title'] + ' ' + df['Area']


df7 = df[df["ConsultationDate"] >= seven_days_ago]   


# set nice colors

cmap = plt.get_cmap("Set2")
titles = df7['Title'].unique()
num_colors = len(titles)
colors = [cmap(i / num_colors) for i in range(num_colors)]
color_mapping = dict(zip(titles, ["red","blue","green","orange","purple","brown","pink","gray","olive","cyan"][:num_colors]))
if df7.empty:
    print("No data from the last 7 days to plot.")
else:
    # Create plot
    p = (ggplot(df7, aes(x="ConsultationDate", 
                         y="Queue days", 
                         color="Title"))
         + geom_line()
         + geom_point()
         + geom_hline(aes(yintercept="CreditDays"), 
                      linetype="dashed", 
                      color="red")
         + labs(
             x="Date of scraping",
             y="Queue days"
         )
         + theme_bw() 
         + scale_color_manual(values=color_mapping) 
         + theme(axis_text_x=element_text(rotation=45, hjust=1))
    )



p.save("apartment_queue.pdf", width=8, height=6)
