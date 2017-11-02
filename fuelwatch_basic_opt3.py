

from datetime import datetime
from lxml import objectify, etree
from urllib.parse import urlencode
import requests


from requests.exceptions import ConnectionError, Timeout, HTTPError, RequestException

debug = False

list_data = []


def gen_urls_list(products_list, regions_list, brands_list):

    url_params = {}  # Dictionary
    url_list = []  # List

    # get Regions
    for each_region in regions_list:
        # print("Region" + str(each_region))
        url_params['Region'] = each_region
        # print(url_params)

        # get brands
        for each_brand in brands_list:
            # print("Brand" + str(each_brand))
            url_params['Brand'] = each_brand
            # print(url_params)

            for each_product in products_list:
                # print("Product" + str(each_product))
                url_params['Product'] = each_product
                # print(url_params)

                base_url = "http://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?"
                final_url = base_url + urlencode(url_params)

                print(final_url)

                url_list.append(final_url)

    # print(url_list)
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

    # Some elements in the XML string are empty, using try: as a lazy way of dealing with them.
    try:
        if root.channel.item:
            list_data_temp = []
            list_data_all = []
            for e in root.channel.item:

                dict_data = {
                    'Price': e.price.text,
                    'Location': e.location.text,
                    'Address': e.address.text,
                    'phone': e.phone.text,
                    'brand': e.brand.text,
                    'date': e.date.text
                }

                if debug:
                    print(dict_data)

                list_data.append(dict_data)

            # list_data_all.append(list_data_temp)

            # return list_data_all

    except Exception as e:
        # print(e)
        return None


def gen_html():

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

                                  <title>Fuel Watch</title>

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
                                        {}
                                    </tbody>
                                </table>
                              </body>
                              </html>""".format(table_content)

    # Open File to write HTML Data
    # using "With"  statement , no need to close the file explictly
    with open('fuelwatch_basic_opt3.html', 'w') as f:
        f.write(template)


def run():
    products = [1]
    regions = [25, 26, 27]
    brands = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    suburbs = ["SUBIACO"]

    # 1. Generate URLs
    url_list = gen_urls_list(products, regions, brands)

    # 2. Get FuelWatch xml data for each URL
    for each_url in url_list:
        raw_xml_data = get_fuelwatch_xml(each_url)

        # 3. Clean the raw xml data for use with lxml/Objectify
        cleaned_fuelwatch_xml_data = clean_fuelwatch_xml_data(raw_xml_data.content)

        # 4. Create the table content (as LIST)
        gen_html_table_listdata(cleaned_fuelwatch_xml_data)

    # 5. Create the HTML output
    gen_html()


run()

"""
Comments on above code/approach:
- ?

"""