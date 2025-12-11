from report.plotandmail import plot_save

from scraper.listings import scrape_listings

def main():
    scrape_listings()
    plot_save()

if __name__ == "__main__":
    main()