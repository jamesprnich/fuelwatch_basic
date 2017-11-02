

from datetime import datetime
from lxml import objectify, etree
from urllib.parse import urlencode
import requests


from requests.exceptions import ConnectionError, Timeout, HTTPError, TooManyRedirects, RequestException


def clean_fuelwatch_xml_data(xml_string):
    """
    Replaces hyphens with underscores in element names

    :param xml_string:
    :return:
    """

    doc = etree.XML(xml_string)
    for e in doc.xpath('//*[contains(local-name(),"-")]'):
        e.tag = e.tag.replace('-', '_')

    return etree.tostring(doc)


# def get_fuelwatch_xml(date, product_code=None, brand_code=None, suburb_name=None):
#     url_params = {}  # Dictionary
#     if date:
#         print(date)
#         url_params['Day'] = str(date)
#     if product_code:
#         url_params['Product'] = product_code
#     if brand_code:
#         url_params['Brand'] = brand_code
#     if suburb_name:
#         url_params['Suburb'] = suburb_name
#
#     # Example resultant url_params = {'Day': '07/10/2017', 'Product': 1}
#     # Note: it appends each new key:value to the dictionary automagically :) lol!
#
#     # Generate XML URL
#     base_url = "http://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?"
#     final_url = base_url + urlencode(url_params)
#
#     print(final_url)
#
#     try:
#         # Get the xml file from the provided URL
#         data = requests.get(final_url)
#
#         # Clean the xml - the fuelwatch xml file has element names containing hyphens. This swaps them for underscores. This is required as we are using lxml objectify.
#         clean_data = clean_fuelwatch_xml_data(data.content)
#
#         print(clean_data)
#
#         # Objectify (http://lxml.de/objectify.html) the xml string
#         root = objectify.fromstring(clean_data)
#
#         # Some elements in the XML string are empty, using try: as a lazy way of dealing with them.
#         list_data = []
#         try:
#             for e in root.channel.item:
#
#                 dic_data = {
#                     'Price': e.price.text,
#                     'Location': e.location.text,
#                     'Address': e.address.text,
#                     'phone': e.phone.text,
#                     'brand': e.brand.text,
#                     'date': e.date.text
#                 }
#
#                 print(dic_data)
#
#                 list_data.append(dic_data)
#                 list_data = sorted(list_data, key=lambda k: k['Price'])
#
#             return list_data
#
#         except Exception as e:
#             print(e)
#     except Timeout:
#         print("error - timeout")
#     except TooManyRedirects:
#         print("error - toomanyredirects")
#     except HTTPError:
#         print("error - http error")
#     except ConnectionError:
#         print("error - connection error")
#     except RequestException as e:
#         # Other error.
#         print(e)
#
#
# def get_fuelwatch_xml2(url_list):
#
#     for each_url in url_list:
#         print(each_url)
#         try:
#             # Get the xml file from the provided URL
#             data = requests.get(each_url)
#
#             # Clean the xml - the fuelwatch xml file has element names containing hyphens. This swaps them for underscores. This is required as we are using lxml objectify.
#             clean_data = clean_fuelwatch_xml_data(data.content)
#
#             # print(clean_data)
#
#             # Objectify (http://lxml.de/objectify.html) the xml string
#             root = objectify.fromstring(clean_data)
#
#             # Some elements in the XML string are empty, using try: as a lazy way of dealing with them.
#             try:
#                 list_data = []
#                 for e in root.channel.item:
#
#                     dic_data = {
#                         'Price': e.price.text,
#                         'Location': e.location.text,
#                         'Address': e.address.text,
#                         'phone': e.phone.text,
#                         'brand': e.brand.text,
#                         'date': e.date.text
#                     }
#
#                     # print(dic_data)
#
#                     list_data.append(dic_data)
#                     list_data = sorted(list_data, key=lambda k: k['Price'])
#
#                 return list_data
#
#             except Exception as e:
#                 print(e)
#                 pass
#         except Timeout:
#             print("error - timeout")
#         except TooManyRedirects:
#             print("error - toomanyredirects")
#         except HTTPError:
#             print("error - http error")
#         except ConnectionError:
#             print("error - connection error")
#         except RequestException as e:
#             # Other error.
#             print(e)


def get_fuelwatch_xml3(url):

    try:
        # Get the xml file from the provided URL
        xml_data = requests.get(url)

        # Clean the xml - the fuelwatch xml file has element names containing hyphens. This swaps them for underscores. This is required as we are using lxml objectify.
        clean_data = clean_fuelwatch_xml_data(xml_data.content)

        # Objectify (http://lxml.de/objectify.html) the xml string
        root = objectify.fromstring(clean_data)

        # Some elements in the XML string are empty, using try: as a lazy way of dealing with them.
        try:
            if root.channel.item:
                list_data = []
                for e in root.channel.item:

                    dict_data = {
                        'Price': e.price.text,
                        'Location': e.location.text,
                        'Address': e.address.text,
                        'phone': e.phone.text,
                        'brand': e.brand.text,
                        'date': e.date.text
                    }

                    print(dict_data)

                    list_data.append(dict_data)
                    # Need to understand what this does
                    list_data = sorted(list_data, key=lambda k: k['Price'])

                    table_body = ''

                    for i in list_data:
                        table_row = "<tr><td>{Price}</td><td>{Location}</td><td>{Address}</td><td>{phone}</td><td>{brand}</td><td>{date}</td></tr>".format(
                            **i)
                        table_body += table_row
                        print(table_body)

                return list_data

        except Exception as e:
            print(e)
            return None

    except Timeout:
        print("error - timeout")
    except TooManyRedirects:
        print("error - toomanyredirects")
    except HTTPError:
        print("error - http error")
    except ConnectionError:
        print("error - connection error")
    except RequestException as e:
        # Other error.
        print(e)


def gen_html(fw_data):
    # Declare a string to hold table row data
    table_body = ''

    for i in fw_data:
        table_row = "<tr><td>{Price}</td><td>{Location}</td><td>{Address}</td><td>{phone}</td><td>{brand}</td><td>{date}</td></tr>".format(**i)
        table_body += table_row

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
                              </html>""".format(table_body)

    # Open File to write HTML Data
    # using "With"  statement , no need to close the file explictly
    with open('fuelwatch_basic.html', 'w') as f:
        f.write(template)


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

                # print(final_url)

                url_list.append(final_url)

    # print(url_list)
    return url_list


def do_it_all():
    products = [1]
    regions = [25, 26, 27]
    brands = [2, 3, 4, 5]
    suburbs = ["SUBIACO"]

    # Generate URLs
    url_list = gen_urls_list(products, regions, brands)

    # Get FW xml data for each URL
    fw_data = []
    for each_url in url_list:
        fw_data_temp = get_fuelwatch_xml3(each_url)
        # print(fw_data_temp)
        if fw_data_temp is not None:
            fw_data.append(fw_data_temp)

    # print(type(fw_data))

    # for each in fw_data:
    #     print(each)

    #gen_html(fw_data)


do_it_all()

#urls_list = gen_urls_list()
#fw_data = get_fuelwatch_xml2(urls_list)
# print(list_data)
#fw_data = get_fuelwatch_xml((datetime.now().today().strftime("%d/%m/%Y")), product_code=2)

#gen_html(fw_data)
