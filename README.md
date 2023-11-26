<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/MatRos-sf/Bet-Game-Premier-League">
    <img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/blob/main/BetGame_PremierLeague/media/website_img/logo.png" alt="Logo" width="180" height="180">
  </a>

<h3 align="center">Bet Game Premier League</h3>

  <p align="center">
    <a href="https://github.com/MatRos-sf/Bet-Game-Premier-League/issues">Report Bug</a>
    ·
    <a href="https://github.com/MatRos-sf/Bet-Game-Premier-League/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#features">Features</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#screenshot">Screenshot</a></li>
    <li><a href="#source">Source</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Bet Game Premier League is a straightforward platform for betting on Premier League matches. Stay updated on match information and compete with other players.
### Features
* Users can set bets on matches. If they win, they earn points. Additionally, users have the option to pay for bets using their earned points, allowing them to accumulate even more.
* Points System
* Individual User Statistics
* Create events and invite your friends to join in the excitement.
* Team-specific statistics
* Support for teams
* Access match information, including the current season's performance, recent team matches, and form.
* Fixture and match results


<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Django][Django]][Django-url]
* [![Python][Python]][Python-url]
* [![Requests][Requests]][Requests-url]
* [![Django_Rest_Framework][Django_Rest_Framework]][Django_Rest_Framework-url]
* [![Factory_Boy][Factory_Boy]][Factory_Boy-url]
* [![Parameterized][Parameterized]][Parameterized-url]
* [![JWT][JWT]][JWT-url]


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started
### Prerequisites
Before you begin, kindly create an account to obtain a free API Key from [football-data](https://www.football-data.org/).
This key is essential for connecting with the project.

### Installation
1. Clone the repo
   ```sh
   git clone https://github.com/MatRos-sf/Bet-Game-Premier-League.git
   ```
2. Create environment
   ```sh
   python3 -m venv venv
   ```
3. Install the package:
   ```sh
   pip install -r requirements.txt
   ```
4. Create `.env` file, and add:
    ```text
    SECRET_KEY= PROJECT_SECRET_KEY
    API_TOKEN=MORE_Prerequisites
    ```
5. Next, you have to pull information about currently season:
    ```sh
    python3 manage.py pull_fd
    ```
6. Finally, you have to set workers
    ```sh
    python3 manage.py set_workers
   ```


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Screenshot

### Home
### Profile

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- More Information -->
## Source
Templates source and inspiration [colorlib](https://colorlib.com).


<!-- CONTACT -->
## Contact

Mateusz Rosenkranz - mateuszrosenkranz@gmail.com

Project Link: [https://github.com/MatRos-sf/Bet-Game-Premier-League](https://github.com/MatRos-sf/Bet-Game-Premier-League)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Django]: https://img.shields.io/badge/Django-3.2-092E20?style=for-the-badge&logo=django
[Django-url]: https://www.djangoproject.com/
[Python]: https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python
[Python-url]: https://www.python.org/
[Requests]: https://img.shields.io/badge/Requests-2.26.0-008080?style=for-the-badge&logo=requests
[Requests-url]: https://docs.python-requests.org/en/latest/
[Django_Rest_Framework]: https://img.shields.io/badge/Django%20Rest%20Framework-3.12-03282C?style=for-the-badge&logo=django
[Django_Rest_Framework-url]: https://www.django-rest-framework.org/
[Factory_Boy]: https://img.shields.io/badge/Factory%20Boy-3.2.0-FF69B4?style=for-the-badge&logo=python
[Factory_Boy-url]: https://factoryboy.readthedocs.io/en/stable/
[Parameterized]: https://img.shields.io/badge/Parameterized-0.8.1-00CED1?style=for-the-badge&logo=python
[Parameterized-url]: https://parameterizedtestcase.readthedocs.io/en/latest/
[JWT]: https://img.shields.io/badge/DRF%20Simple%20JWT-4.9.0-1E90FF?style=for-the-badge&logo=django
[JWT-url]: https://django-rest-framework-simplejwt.readthedocs.io/en/latest/
