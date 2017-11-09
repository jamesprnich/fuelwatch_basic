

from datetime import datetime
from lxml import objectify, etree
from urllib.parse import urlencode
import requests
import itertools


from requests.exceptions import ConnectionError, Timeout, HTTPError, RequestException

debug = False

list_data = []


def gen_urls_list(products_list, regions_list, brands_list):

    # Old way using for loop

    # url_list = []
    # for i in itertools.product(products_list, brands_list, regions_list):
    #     # used *i to convert list/tuple to positional arguments
    #     # final_url = "http://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?Product={}&Brand={}".format(*i)
    #
    #     # print(final_url)
    #     url_list.append("http://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?Product={}&Brand={}".format(*i))
    # -------------

    # New, better way using for list comprehension
    url_list = [
        "http://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?Product={}&Brand={}".format(*i)
        for i in itertools.product(products_list, brands_list, regions_list)
    ]

    print("======")
    print("# of URLs to process: " + str(len(url_list)))
    return url_list


def get_fuelwatch_xml(url):

    try:
        # Get the xml file from the provided URL
        raw_xml_data = requests.get(url)
        return raw_xml_data

    except Timeout:
        print("error - timeout")
    except HTTPError:
        print("error - http error")
    except ConnectionError:
        print("error - connection error")
    except RequestException as e:
        # Other error.
        print(e)


def clean_fuelwatch_xml_data(xml_data):
    """
    Replaces hyphens with underscores in element names

    :param xml_data:
    :return:
    """

    doc = etree.XML(xml_data)
    for each in doc.xpath('//*[contains(local-name(),"-")]'):
        each.tag = each.tag.replace('-', '_')

    return etree.tostring(doc)


def gen_html_table_listdata(cleaned_xml_data):
    """

    :param cleaned_xml_data:
    :return:
    """
    # Objectify (http://lxml.de/objectify.html) the xml string/data
    root = objectify.fromstring(cleaned_xml_data)

    counter = 0
    # Some elements in the XML string are empty, using try: as a lazy way of dealing with them.

    if hasattr(root.channel, 'item'):
        for e in root.channel.item:

            dict_data = {
                'Price': e.price.text,
                'Location': e.location.text,
                'Address': e.address.text,
                'phone': e.phone.text,
                'brand': e.brand.text,
                'date': e.date.text
            }

            counter = counter + 1

            if debug:
                print(dict_data)

            list_data.append(dict_data)

    return counter


def gen_html(total_count):

    # print(table_content_listdata)

    # Sort list data by Price
    list_data_sorted = sorted(list_data, key=lambda k: k['Price'])

    if debug:
        print(list_data_sorted)

    table_content = ''
    for i in list_data_sorted:
        table_row = "<tr><td>{Price}</td><td>{Location}</td><td>{Address}</td><td>{phone}</td><td>{brand}</td><td>{date}</td></tr>".format(**i)
        table_content = table_content + table_row

        if debug:
            print(table_content)

    # Create Template to hold HTML Data
    template = """<html>
                              <head>

                                  <title>Fuel Watch</title>{1}

                                    <script src='https://code.jquery.com/jquery-3.2.1.slim.min.js' integrity='sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN' crossorigin='anonymous'></script>

                                    <link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css' integrity='sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M' crossorigin='anonymous'>
                                    <script src='https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.11.0/umd/popper.min.js' integrity='sha384-b/U6ypiBEHpOf/4+1nzFpr53nxSS+GLCkfwBdFNTxtclqqenISfwAzpKaMNFNmj4' crossorigin='anonymous'></script>
                                    <script src='https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/js/bootstrap.min.js' integrity='sha384-h0AbiXch4ZDo7tp9hKZ4TsHbi047NrKGLO3SEJAg45jXxnGIfYzk4Si90RDIqNm1' crossorigin='anonymous'></script>
                              </head>

                              <body>
                                  <h2>"Fuel Prices For all metro regions" </h2>

                                   <table border = "1" class='table table-sm'>
                                   <thead>
                                          <tr>
                                             <th>Price</th>
                                             <th>Location</th>
                                             <th>Address</th>
                                             <th>Phone</th>
                                             <th>Brand</th>
                                             <th>Date</th>
                                           </tr>
                                     </thead>
                                    <tbody> 
                                        {0}
                                    </tbody>
                                </table>
                              </body>
                              </html>""".format(table_content, total_count)

    # Open File to write HTML Data
    # using "With"  statement , no need to close the file explictly
    with open('fuelwatch_basic_opt5.html', 'w') as f:
        f.write(template)


def run():
    products = [1, 2, 3]
    regions = [25, 26, 27]
    brands = [1, 2, 3, 4, 5]
    # suburbs = ["SUBIACO"]

    total_count = 0

    # 1. Generate URLs
    url_list = gen_urls_list(products, regions, brands)

    url_list_count_total = len(url_list)

    # 2. Get FuelWatch xml data for each URL

    # for each_url in url_list:
    #     url_list_counter += 1

    for url_list_counter, each_url in enumerate(url_list):
        print("Processing " + str(url_list_counter) + " of " + str(url_list_count_total))
        raw_xml_data = get_fuelwatch_xml(each_url)

        # 3. Clean the raw xml data for use with lxml/Objectify
        cleaned_fuelwatch_xml_data = clean_fuelwatch_xml_data(raw_xml_data.content)

        # 4. Create the table content (as LIST)
        row_count = gen_html_table_listdata(cleaned_fuelwatch_xml_data)

        if row_count:
            total_count = total_count + row_count

    # 5. Create the HTML output
    gen_html(total_count)


run()

"""
Comments on above code/approach:
- Attempted to break code into various functions vs one big function

"""