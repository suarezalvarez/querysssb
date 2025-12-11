import pandas as pd
from datetime import datetime, timedelta
from plotnine import ggplot, aes, geom_line, geom_point, geom_hline, labs, theme_bw, theme, element_text, scale_color_manual
import matplotlib.pyplot as plt

# read csv

def plot_save():
    """
    Generate a 7-day plot of SSSB apartment queue days and save it to PDF.

    This function loads the scraped apartment dataset from
    `storage/apartments.csv`, filters entries from the last 7 days, and produces
    a line plot showing the queue days for each available apartment over time.
    A dashed horizontal line indicates the user's current number of credit days.
    The plot is saved to `storage/apartment_queue.pdf`.

    Steps performed:
    1. Load the dataset and parse date columns.
    2. Convert numeric columns (e.g., CreditDays).
    3. Add Area to the apartment Title for easier identification.
    4. Filter the data to the last 7 days.
    5. Generate one color per unique apartment title (max 10 fallback colors).
    6. Produce a ggplot-style line plot using plotnine.
    7. Save the final figure as a PDF.

    Notes
    -----
    - If no entries exist within the last 7 days, the function prints a
      message and does not generate a plot.
    - The color palette uses Matplotlib’s Set2 colormap combined with a fixed
      fallback palette.
    - The PDF is always overwritten.

    Output
    ------
    storage/apartment_queue.pdf : PDF
        A PDF file containing the generated 7-day queue plot.
    """
    
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



    p.save("storage/apartment_queue.pdf", width=8, height=6)
