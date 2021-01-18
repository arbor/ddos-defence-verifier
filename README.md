**DDoS Defence Verifier Tool for Arbor Sightline/TMS and MSSPs**
(aka DDV)

Benefits to using DDV:
1. A consolidated testing platform for individual or multiple Sightline Deployments
2. Routine fire-drills conducted at the click of a button
    - Verify that the Entity under Test (Webserver, DNS server, etc) is responding as expected
    - Simulate a small DDoS “attack” (from your own ‘botnets’)
        - too small to do damage, large enough for DoS Host Detection
    - Check if Sightline raises and alert, starts a TMS mitigation, and uses correct Counter Measures (CMs)
3. Early detection of SL+TMS deployment issues that could jeopardise mitigation of real attacks
    - Routers:
        - Incorrect flow export timers, too large sampling rates or no flows at all
    - Sightline:
        - Misconfigured network boundaries or external interfaces
    - TMS:
        - Diversion/ReInjection issues


DDV Method of Operation:
 - The tool basically lets you create frequent and automated “fire drills”  
 - You define:
     - Organisation (company) under test (OuT)
     - Entities (targets) under test (EuT)
     - Traffic Generators (TG) (aka bots)
        - Any VM/VPS running Linux
            - Attacker (DDV-TG-A)
            - Verifier (DDV-TG-V)
        - Each TG sends small pps of ‘attack’ and/or legit (verification) data to the EuT
 - The DDV-Console checks if Sightline (via the Rest API) has:
     - Raised a DoS alert for the simulated ‘attack’ traffic, with expected DoS misuse types
     - if a TMS auto-mitigation was triggered or not
        - how effective said mitigation is on the malicious traffic  (blocked rate)
        - while legitimate traffic is allowed to pass as expected (success rate)


Sightline Configuration using REST API:
 - DDV-C creates the following “test infrastructure” on the Sightline Leader:
    - DDV Managed Objects (MOs) – to match the EuT IPs
    - Shared Host Detection Settings (SHDS) for DDV MOs, so they will predictably trigger DoS alerts with small amount of attack pps rates from Traffic Generator (TG)
    - DDV Mitigation Template with CMs that will be enabled automatically based on DoS alerts
        - TCP SYN, UDP R/A
    - Only manual steps required on SL CLI: 
        - Generate REST API key
    - Only manual steps required on SL GUI: 
        - link DDV Mitigation Template to “TMS Group”, enable “Announce Route”




DDV-Console Setup Steps:
1. Clone the git repository to your desired location, which will be the main GUI, or Console (DDV-C):
```bash
git clone https://github.com/markcampbellza/ddos-defence-verifier.git
 ```

2. Change to the directory containing the main python script, ddv-c.py, and run it:
```bash
python3 ddv-c.py 
```

- You should see an output similar to the following:

```
    * Serving Flask app "ddv-c" (lazy loading)
    * Environment: production
       WARNING: This is a development server. Do not use it in a production deployment.
       Use a production WSGI server instead.
    * Debug mode: on
    * Running on https://0.0.0.0:2020/ (Press CTRL+C to quit)
    * Restarting with stat
    * Debugger is active!
    * Debugger PIN: 272-128-100
```

- If you are getting a whole lot of errors for required python packages, ensure you have these installed:
```bash
sudo pip3 install -r requirements.txt
```

3. Login to the DDV-C GUI:
```
https://127.0.0.1:2020
```
- default username/password: admin/ddv

4. Configuration Steps on the DDV-C GUI:
 - Define Traffic Generator Agents (TG Attacker or Verifier)
    - Automated TG-Agents using VULTR VPS and API:
        - TG-Agents > VPS
    - Manual TG-Agents using your own Linux servers:
        - TG-Agents > New
        - TG-Agents > Status
 - Define your Organisation under Test (OuT)
    - Could be a single organisation or multiple organisations
    - OuT > New
    - OuT > Status
 - Define your Entity under Test (EuT)
     - EuT > New
     - EuT > Status
 - Define your Attack and/or Verifier Tasks
     - A-Tasks > New
     - A-Tasks > Status
     - V-Tasks > New
     - V-Tasks > Status
 - Verify that the OuT Sightline has MOs, SHDS, Mitigation Templates defined
    - OuT > SL-Config
 - Verify DDV Settings
    - OuT > Status
 - Run complete set of tests to verify your Sightline+TMS DDoS deployment
    - OuT > Run
    
    
  
    
Non-VPS DDV Traffic Generator (DDV-TG-x) Setup Steps:
1. Copy the following files to any appropriate directory on your DDV-TG (linux VPS host)
 - ddv-tg-x/ddv-tg-x.py
 - ddv-tg-x/ddv_tg_x_scapy.py

- To run the DDV-TG as an Attacker, select the A role

```bash
sudo python ddv-tg-x.py -r A
```

- To run the DDV-TG as a Verifier, select the V role

```bash
sudo python ddv-tg-x.py -r V
```

* ddv-tg-x.py must be run as root, this is to allow the generation of packets

- To ensure these scripts keep running in the background, even when you disconnect from the terminal:
```bash
sudo nohup python ddv-tg-x.py -r A &
```
```bash
sudo nohup python ddv-tg-x.py -r V &
```

- If you are getting a whole lot of errors for required python packages, ensure you have these installed:
```bash
sudo pip install flask (or apt-get install python-flask)
sudo pip install pandas (or apt-get install python-pandas)
sudo pip install requests (or apt-get install python-requests)
sudo pip install pyopenssl
sudo pip install --pre scapy[basic]
```
