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
        <li><a href="#docker">Docker</a></li>
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
* Stats about bets


<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Django][Django]][Django-url]
* [![Python][Python]][Python-url]
* [![Django_Rest_Framework][Django_Rest_Framework]][Django_Rest_Framework-url]




<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started
### Prerequisites
Before you begin, kindly create an account to obtain a free API Key from [football-data](https://www.football-data.org/).
This key is essential for connecting with the project.

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/MatRos-sf/Bet-Game-Premier-League.git
   ```
2. Create a virtual environment:
   ```sh
   python3 -m venv venv
   ```
3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```
4. Build the `.env` file using the provided template in the `sample_env` file.

5. Execute the `migration` command:
    ```sh
    python3 manage.py migrate
    ```
6. Additionally, retrieve information about the current season and set up workers:
    ```sh
    python3 manage.py pull_fd
   python3 manage.py set_workers
    ```
   If you want, you have to download information about previous seasons:
    ```sh
    python3 manage.py pull_history
   ```
### Docker
You can also run the project using Docker. Docker configuration files are stored in the `.docker` directory.
Remember to set the `DB_HOST` variable in the `.env` file; it should be the hostname.

To get started, use the following command:
```shell
docker-compose up --build
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Screenshot
<img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/assets/59665130/a51c52fb-dfcb-4f4c-9164-ce9976270e44" width="45%"></img> <img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/assets/59665130/34a0d150-0cae-4e5b-b72c-85249b61c31c" width="45%"></img> <img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/assets/59665130/a29e5e0c-6dd1-428e-a2e2-ceaa9dd8a0e1" width="45%"></img> <img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/assets/59665130/d4d686cf-3acc-4889-b218-8ec7adb95f5c" width="45%"></img> <img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/assets/59665130/a6134ae7-0107-44d2-a28a-081da06eeb64" width="45%"></img> <img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/assets/59665130/17f2bff5-1107-4a37-bc57-5a4dd0c45193" width="45%"></img> <img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/assets/59665130/715d3cda-a83e-42ad-b473-07906b4d5522" width="45%"></img> <img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/assets/59665130/fc44b1f4-3620-4c54-a016-6f6dbf870a48" width="45%"></img> <img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/assets/59665130/973acfb0-bf5c-413b-b3c7-53a3b94aee25" width="45%"></img> <img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/assets/59665130/333a8ce3-2887-4cd9-bc06-3cda0d748b98" width="45%"></img> <img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/assets/59665130/b5e0887c-3058-4b22-b89b-85467bbc4a9f" width="45%"></img> <img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/assets/59665130/5e8de7ec-0c38-453b-bf0d-db300b52101e" width="45%"></img> <img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/assets/59665130/3e3cb477-bd67-49e0-8a56-a2424a8d7061" width="45%"></img> <img src="https://github.com/MatRos-sf/Bet-Game-Premier-League/assets/59665130/06bbba6c-a002-49c6-b123-1c1dafc75548" width="45%"></img>

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
[Django]: https://img.shields.io/badge/Django-4.2.7-092E20?style=for-the-badge&logo=django
[Django-url]: https://www.djangoproject.com/
[Python]: https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python
[Python-url]: https://www.python.org/
[Requests]: https://img.shields.io/badge/Requests-2.26.0-008080?style=for-the-badge&logo=requests
[Requests-url]: https://docs.python-requests.org/en/latest/
[Django_Rest_Framework]: https://img.shields.io/badge/Django%20Rest%20Framework-3.14.0-03282C?style=for-the-badge&logo=django
[Django_Rest_Framework-url]: https://www.django-rest-framework.org/
[Factory_Boy]: https://img.shields.io/badge/Factory%20Boy-3.2.0-FF69B4?style=for-the-badge&logo=python
[Factory_Boy-url]: https://factoryboy.readthedocs.io/en/stable/
[Parameterized]: https://img.shields.io/badge/Parameterized-0.8.1-00CED1?style=for-the-badge&logo=python
[Parameterized-url]: https://parameterizedtestcase.readthedocs.io/en/latest/
