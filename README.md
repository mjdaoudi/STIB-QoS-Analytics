# STIB : Quality of Service Assessment

## About The Project

![STIB QoS Analytics][product-screenshot]

The project is done within the context of the [Data Mining](https://www.ulb.be/en/programme/2021-info-h423) class given by Prof. Mahmoud Sakr at the ULB. It aims at supporting the brussels public transport system at asssessing the quality of its network using data mining solutions. Further explanation can be found within the `hack_my_ride.pdf` file.

To summarize, three inputs were provided :

- General Transit Feed Specification (GTFS) files were providing the theoretical schedule.
- JSONs observations of vehicle positions every 30sec across the network.
- Shapefiles regarding the geography of the network (stops and lines).

As such, two main tasks aimed at clustering specific times of the day to chose which metrics to assess and evaluating which stops were major delayers and catchers across all the network :

- Change point detection - PELT modeling for intraday clustering
- Frequent pattern mining - FP growth on slopes of the median delay evolution through sequences of stops in a specific lines for detecting problematic segments in the network

Finally to visualise the reuslts, a dashboard has been develop to visualize the results.

### Built With

[![python][python]][python-url]
[![Plotly][pl]][plotly-url]
[![pandas][pandas]][pandas-url]
[![numpy][numpy]][numpy-url]

## Getting Started

This repo contains all the necessary functions to reproduce the results. However, the dashboard only will be covered within this readme. For further explainations, feel free to reach me at *mehdi.jdaoudi@ulb.be*.

1. Feel free to contact me to get the data files. Clone the repo and create a `data` folder containing the data I sent.
2. Install requirements using `pip install -r requirements.txt`.
3. Launch the dashboard by going to the root of the project in a terminall session and running `python app.py`
4. Enjoy on your localhost ! 😊

## Visualisations

![STIB QoS Analytics][screen1]

![STIB QoS Analytics][screen2]

![STIB QoS Analytics][screen3]

![STIB QoS Analytics][screen4]

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

## Contact

- Hakim Amri: hakim.amri@ulb.be
- Rania Baguia: rania.baguia@ulb.be
- Abdelmoumen Oumahi : abdelmoumen.oumahi@ulb.be
- Mehdi Jdaoudi : mehdi.jdaoudi@ulb.be

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[python]: https://img.shields.io/badge/python-000000?style=for-the-badge&logo=python&logoColor=white
[python-url]: https://www.python.org
[pandas]: https://img.shields.io/badge/pandas-000000?style=for-the-badge&logo=pandas&logoColor=white
[pandas-url]: https://pandas.pydata.org
[numpy]: https://img.shields.io/badge/numpy-000000?style=for-the-badge&logo=numpy&logoColor=white
[numpy-url]: https://numpy.org
[pl]: https://img.shields.io/badge/plotly-dash-20232A?style=for-the-badge&logo=plotly&logoColor=61DAFB
[plotly-url]: https://plotly.com
[pl]: https://img.shields.io/badge/plotly-dash-20232A?style=for-the-badge&logo=plotly&logoColor=61DAFB
[product-screenshot]: readme_images/product.png
[screen1]: readme_images/screen1.png
[screen2]: readme_images/screen2.png
[screen3]: readme_images/screen3.png
[screen4]: readme_images/screen4.png
