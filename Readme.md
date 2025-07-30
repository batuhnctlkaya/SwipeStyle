This project is a web app that recomends products in Turkish market places based on users need

The main interaction goes like 
    - User Clicks a product type ex. "Headphones"
    - Agent asks generic questions first ex. "Do you like earbuds or headsets"
    - User makes their choice by clicking which one they like
    - Agent starts to ask more specific questions about users want
    - When agent is sure about %90 what the user needs it provides different products ranging different price points

All agent code will be in the app/agent.py
Website side things will be under the website folder
Category specifications like Headphones may be wireless, have ANC or not, Bass based, microphone quality all this information will be on the categories.json file 

and finally with run.py all the web app will be available to use.