

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


def get_fuelwatch_xml(date, product_code=None, brand_code=None, suburb_name=None):
    url_params = {}  # Dictionary
    if date:
        print(date)
        url_params['Day'] = str(date)
    if product_code:
        url_params['Product'] = product_code
    if brand_code:
        url_params['Brand'] = brand_code
    if suburb_name:
        url_params['Suburb'] = suburb_name

    # Example resultant url_params = {'Day': '07/10/2017', 'Product': 1}
    # Note: it appends each new key:value to the dictionary automagically :) lol!

    # Generate XML URL
    base_url = "http://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?"
    final_url = base_url + urlencode(url_params)

    print(final_url)

    try:
        # Get the xml file from the provided URL
        data = requests.get(final_url)

        # Clean the xml - the fuelwatch xml file has element names containing hyphens. This swaps them for underscores. This is required as we are using lxml objectify.
        clean_data = clean_fuelwatch_xml_data(data.content)

        print(clean_data)

        # Objectify (http://lxml.de/objectify.html) the xml string
        root = objectify.fromstring(clean_data)

        # Some elements in the XML string are empty, using try: as a lazy way of dealing with them.
        list_data = []
        try:
            for e in root.channel.item:

                dic_data = {
                    'Price': e.price.text,
                    'Location': e.location.text,
                    'Address': e.address.text,
                    'phone': e.phone.text,
                    'brand': e.brand.text,
                    'date': e.date.text
                }

                print(dic_data)

                list_data.append(dic_data)
                list_data = sorted(list_data, key=lambda k: k['Price'])

            return list_data

        except Exception as e:
            print(e)
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


def gen_html(list_data):
    # Declare a string to hold table row data
    Table_body = ''

    for i in list_data:
        table_row = "<tr><td>{Price}</td><td>{Location}</td><td>{Address}</td><td>{phone}</td><td>{brand}</td><td>{date}</td></tr>".format(
            **i)
        Table_body += table_row

    # Create Template to hold HTML Data
    template = """<html>
                              <head>
                              </head>
    
                              <body>
                                  <h2>"Fuel Prices For all metro regions" </h2>
    
                                   <table border = "1">
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
                                    <tbody> {}
                                    </tbody>
                                </table>
                              </body>
                              </html>""".format(Table_body)

    # Open File to write HTML Data
    # using "With"  statement , no need to close the file explictly
    with open('fuelwatch_basic.html', 'w') as f:
        f.write(template)


xml_data = get_fuelwatch_xml((datetime.now().today().strftime("%d/%m/%Y")), product_code=2, brand_code=1, suburb_name="SUBIACO")

gen_html(xml_data)
