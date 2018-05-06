import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import csv
##
#This code scrapes the reviews of the currys website only for the freezers category
##

def parse_review(review,product_details):

    review_dict = dict()

    stars = review.find('div', attrs={"class": "overall_score_stars"})['title']
    name = review.find('h4', attrs={"class": "attribution-name"}).get_text()


    attribution_details = review.find('h5', attrs={"class": "attribution-details"})
    location_elem = attribution_details.find('span', attrs={"class": "location"})
    location_text = "Empty"
    if location_elem is not None:
        location_text = location_elem.text.strip()
    segment = attribution_details.find('span', attrs={"class": "segment"}).text.strip()

    purchase_data_section = review.find('section', attrs={"class": "purchase_date"})
    
    purchase_date = purchase_data_section.find('span', class_="date date_purchase")
    if purchase_date is None:
        purchase_date = purchase_data_section.find('span', class_="date date_delivery")

    purchase_date_text = purchase_date.text.strip()
    publish_date = purchase_data_section.find('span', attrs={"class": "date_publish"}).text.strip()
    

    divTag = review.find_all('dd', attrs={'class': 'pros'})
    length_of_positives[len(divTag)] = length_of_positives[len(divTag)] + 1 if len(divTag) in length_of_positives else 1
    positive_points = []
    for d in divTag:
        positive_points.append(d.text)
        
    divTag = review.find_all('dd', attrs={'class': 'cons'})
    length_of_negatives[len(divTag)] = length_of_negatives[len(divTag)] + 1 if len(divTag) in length_of_negatives else 1
    negative_points = []
    for d in divTag:
        negative_points.append(d.text)

    score_table_rows = review.find("table", class_="scores").find_all("tr")
    category_reviews = []
    for score in score_table_rows:

        category_name = score.find("th").text.strip()
        categories.add(category_name)
        value = score.find("td").text.strip()
        category = dict()
        category["name"] = category_name
        category["value"] = value
        category_reviews.append(category)

    review_dict['product_id'] = product_details["product_id"]
    review_dict['product_name'] = product_details["product_name"]
    review_dict['product_brand'] = product_details["brand_name"]
    review_dict['product_category'] = product_details["category"]
    review_dict['stars'] = stars
    review_dict['name'] = name
    review_dict['location'] = location_text
    review_dict['segment'] = segment
    review_dict['purchase_date'] = purchase_date_text
    review_dict['publish_date'] = publish_date
    review_dict['positive_points'] = positive_points
    review_dict['negative_points'] = negative_points
    review_dict['category_reviews'] = category_reviews
    return review_dict


def read_product_portfolio():

    total_portfolio = list()
    counter = -1
    counter_Fr = 0
    #name of CSV
    with open('products_portfolio.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')
        for row in csvreader:
            counter = counter + 1
            if counter == 0:
                continue
            #Get only specific Category
            if row[4]=="Freezers":
                counter_Fr = counter_Fr + 1
                portfolio_dict = dict()
                portfolio_dict['product_id'] = row[1]
                portfolio_dict['product_name'] = row[3]
                portfolio_dict['category'] = row[4]
                portfolio_dict['brand_name'] = row[5]
                portfolio_dict['deeplink'] = row[10]
                total_portfolio.append(portfolio_dict)

    return total_portfolio

if __name__ == "__main__":
    # define the browser
    # Path to the chromedriver
    browser = webdriver.Chrome(
        executable_path=r"/Users/harisbitsakou/PycharmProjects/Media_And_Web_Analytics/chromedriver")
    product_dixons_specs = read_product_portfolio()
    # it opens and writes the header of the csv file
    with open('product_reviews_freezersha.csv', 'w') as csvfile:
        fieldnames = ["product_id", "product_name", "product_brand", "product_category", "stars", "name", "location",
                      "segment", "purchase_date", "publish_date", "positive_points", "negative_points",
                      "category_reviews"]
        writer = csv.DictWriter(csvfile,delimiter = "|", fieldnames=fieldnames )

        writer.writeheader()
        PRODUCT_COUNTER = -1
        for product in product_dixons_specs:
            PRODUCT_COUNTER = PRODUCT_COUNTER + 1
            #keep truck of crawler
            print(PRODUCT_COUNTER)
            categories = set()
            length_of_positives = dict()
            length_of_negatives = dict()
            empty_array = dict()
            pages = 0
            reviews = 0

            # the url we want to open
            url = u""+product["deeplink"]
            # the browser will start and load the webpage
            browser.get(url)

            # wait 1 second to let the page load everything
            time.sleep(1)

            # load the HTML body
            body = browser.find_element_by_tag_name('body')

            try:
                element = browser.find_element_by_xpath('//*[@id="edr_survey"]')
                browser.execute_script("""
                                var element = arguments[0];
                                element.parentNode.removeChild(element);
                            """, element)
            except:
                print("Didn't have the element")

            # use seleniums' send_keys() function to physically scroll down where we want to click
            body.send_keys(Keys.PAGE_DOWN)

            # search for an element that is called 'customer reviews', which is a button
            # the button can be clicked with the .click() function
            try:
                browser.find_element_by_link_text("Customer reviews").click()
            except:
                #print("no reviews were available")
                no_reviews = dict()
                no_reviews['product_id'] = product["product_id"]
                no_reviews['product_name'] = product["product_name"]
                no_reviews['product_brand'] = product["brand_name"]
                no_reviews['product_category'] = product["category"]
                no_reviews['stars'] = "NR"
                no_reviews['name'] = "NR"
                no_reviews['location'] = "NR"
                no_reviews['segment'] = "NR"
                no_reviews['purchase_date'] = "NR"
                no_reviews['publish_date'] = "NR"
                no_reviews['positive_points'] = "NR"
                no_reviews['negative_points'] = "NR"
                no_reviews['category_reviews'] = "NR"

                writer = csv.writer(csvfile, delimiter="|")#, quoting=csv.QUOTE_MINIMAL
                writer.writerow(no_reviews.values())
                continue

            # scroll further down to collect the reviews and especially click the next button
            body.send_keys(Keys.PAGE_DOWN)

            # #Avoid issue of duplication of reviews
            # time.sleep(1)
            # browser.find_element_by_xpath('//*[@id="embedded_product_reviews_gtw"]/div[2]/span[2]/span[2]/select/option[2]').click()
            # time.sleep(1)

            #define how many times it tried to change page of reviews
            page_change_attempts = 0

            #read the reviews of the page
            while True:
               # print("--------- NEW PAGE --------------")
                pages += 1
                # get the page content for beautiful soup
                html_source = browser.page_source

                # see beautifulsoup
                soup = BeautifulSoup(html_source, 'html.parser')

                #GET each review of the page
                for review in soup.select('article[id*="review_"]'):
                    reviews += 1
                    #print("     --------- NEW REVIEW --------------")
                    review_dict = parse_review(review,product)
                    writer = csv.writer(csvfile, delimiter="|")
                    writer.writerow(review_dict.values())

                #print("--------- END OF NEW PAGE --------------")
                if page_change_attempts >= 3:
                    break

                while True:
                    try:
                        page_change_attempts = page_change_attempts + 1
                        next_button = browser.find_element_by_link_text('Next')
                        next_button.click()
                        page_change_attempts = 0
                        time.sleep(1)
                        break
                    except Exception as e:
                        #print(e)
                        body.send_keys(Keys.PAGE_DOWN)
                        time.sleep(1)
                        #print(page_change_attempts)
                        if page_change_attempts >= 3:
                            break
                        #end of parsing this product


