The model:

    https://drive.google.com/file/d/1O4v1-Ljbu7r4OU6PWm2mTs-ipyccKwCJ/view?usp=sharing

    make sure to put it in the same folder that has poisoned_model_run.py and poisoned_server_browser_bot.py

The images:

    https://drive.google.com/file/d/1Pvq636zhb8ncLgEj7vRfffo6NuoD9kN2/view?usp=sharing

    after extracting the archive, the 'poisoned' and 'clean' directories should be inside the poisoned_server directory


Running the server:
    run poisoned_server.py
    
Running the bot:
    run poisoned_server_browser_bot.py
    note that the server needs to be running inordor for the bot to function

Testing:
    Testing function to test the model's performace depending on noise levels and used methods have been provided in 
    poisoned_testing_functions.py
    call the function in the script or import it 
    example: 
        testing_function(method_analysis=True)
            to test individual method's performances on the same noise level
        testing_function(noise_analysis=True)
            to test the model's performance on different noise levels, using all the methods
