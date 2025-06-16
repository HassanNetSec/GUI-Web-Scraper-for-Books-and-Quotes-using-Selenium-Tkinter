import csv
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

StarRating = {
    'One': 1,
    'Two': 2,
    'Three': 3,
    'Four': 4,
    'Five': 5
}

# GUI Window
window = tk.Tk()
window.title("Web Scraper")
window.geometry("700x500")

# Output box
output_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=25)
output_box.pack(padx=10, pady=10)

def log(message):
    output_box.insert(tk.END, message + '\n')
    output_box.see(tk.END)

def getRating(star: str):
    rating_word = star.replace('star-rating', '').strip()
    return StarRating.get(rating_word, None)

def scrape_books():
    log("Starting book scraping...")

    option = Options()
    option.add_experimental_option('detach', True)
    driver = webdriver.Chrome(options=option)
    wait = WebDriverWait(driver, 10)

    driver.get('https://books.toscrape.com/')

    try:
        with open('books.csv', mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Page', 'Title', 'Price', 'Rating']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            page = 1
            while page <= 3:
                log(f"\n--- Book Page {page} ---")
                books = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//article[@class='product_pod']")))
                for book in books:
                    title = book.find_element(By.XPATH, ".//h3/a").get_attribute("title")
                    price = book.find_element(By.CLASS_NAME, "price_color").text
                    star_class = book.find_element(By.XPATH, ".//p[contains(@class,'star-rating')]").get_attribute("class")
                    rating_num = getRating(star_class)
                    writer.writerow({'Page': page, 'Title': title, 'Price': price, 'Rating': rating_num})
                    log(f"{title} | {price} | Rating: {rating_num}")

                try:
                    next_btn = driver.find_element(By.XPATH, "//li[@class='next']/a")
                    next_btn.click()
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product_pod")))
                    page += 1
                except:
                    break
    finally:
        driver.quit()
        log("Books scraping complete! Saved to books.csv")

def scrape_quotes():
    log("Starting quotes scraping...")

    option = Options()
    option.add_experimental_option('detach', True)
    driver = webdriver.Chrome(options=option)
    wait = WebDriverWait(driver, 10)

    driver.get('https://quotes.toscrape.com/')

    try:
        tag_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "life")))
        tag_link.click()

        quotes_data = []
        page = 1
        while True:
            log(f"\n--- Quotes Page {page} ---")
            quote_boxes = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "quote")))

            for q in quote_boxes:
                text = q.find_element(By.CLASS_NAME, "text").text
                author = q.find_element(By.CLASS_NAME, "author").text
                tags = [tag.text for tag in q.find_elements(By.CLASS_NAME, "tag")]
                quotes_data.append({'Text': text, 'Author': author, 'life': ", ".join(tags)})
                log(f"{text} — {author} | Tags: {tags}")

            try:
                next_btn = driver.find_element(By.XPATH, "//li[@class='next']/a")
                next_btn.click()
                page += 1
            except:
                break

        with open("quotes_life.csv", "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Text", "Author", "life"])
            writer.writeheader()
            writer.writerows(quotes_data)
    finally:
        driver.quit()
        log("Quotes scraping complete! Saved to quotes_life.csv")

# Buttons
button_frame = tk.Frame(window)
button_frame.pack()

ttk.Button(button_frame, text="Scrape Books", command=lambda: threading.Thread(target=scrape_books).start()).pack(side=tk.LEFT, padx=10)
ttk.Button(button_frame, text="Scrape Life Quotes", command=lambda: threading.Thread(target=scrape_quotes).start()).pack(side=tk.LEFT, padx=10)

window.mainloop()
