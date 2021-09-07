# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()

value = None
num_guesses = None
current_guess = None
pwm_LED = None
pwm_buzzer = None

# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    #print("menu...")
    global end_of_game, value, num_guesses, current_guess
    end_of_game = False
    try:
        GPIO.remove_event_detect(btn_increase)
        GPIO.remove_event_detect(btn_submit)
    except:
        pass

    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":

        GPIO.add_event_detect(btn_increase, edge=GPIO.RISING, callback=btn_increase_pressed, bouncetime=300)
        GPIO.add_event_detect(btn_submit, edge=GPIO.FALLING, callback=btn_guess_pressed, bouncetime=300)
        
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        num_guesses = 0
        current_guess = -1
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    #print("display scores...")
    # print the scores to the screen in the expected format
    # print out the scores in the required format
    print("There are {} scores. Here are the top 3!".format(count))
    for x in range(3):
        print(str(x+1) + " - " + raw_data[x][0] + " took " + str(raw_data[x][1]) + " guesses")

# Setup Pins
def setup():
    #print("setup...")
    global pwm_LED, pwm_buzzer
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    # Setup regular GPIO
    for x in range(3):
        GPIO.setup(LED_value[x], GPIO.OUT)
        GPIO.output(LED_value[x], GPIO.LOW)
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buzzer, GPIO.OUT)
    GPIO.setup(LED_accuracy, GPIO.OUT)
    # Setup PWM channels
    pwm_LED = GPIO.PWM(LED_accuracy, 10000)
    pwm_LED.start(0)
    pwm_buzzer = GPIO.PWM(buzzer, 1)
    pwm_buzzer.start(0)
    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_increase, edge=GPIO.RISING, callback=btn_increase_pressed, bouncetime=300)
    GPIO.add_event_detect(btn_submit, edge=GPIO.FALLING, callback=btn_guess_pressed, bouncetime=300)

# Load high scores
def fetch_scores():
    #print("fetch_scores...")
    # get however many scores there are
    score_count = eeprom.read_byte(0)

    # Get the scores
    temp = eeprom.read_block(0,13)[1:]
    scores = []

    # convert the codes back to ascii
    for idx in range(3):
        if temp[idx*4] != 0 :
            name = chr(temp[idx*4]) + chr(temp[idx*4 + 1]) + chr(temp[idx*4 + 2])
        else:
            name = "N/A"
        scores.append([name,temp[idx*4 + 3]])

    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    #print("save_scores...")
    global name, num_guesses, end_of_game
    # fetch scores
    score_count, scores = fetch_scores()
    # include new score
    scores.append([name,num_guesses])
    num_guesses = 0
    # sort
    scores.sort(key=lambda x: x[1])
    # update total amount of scores
    score_count += 1
    data_to_write = [score_count]
    # write new scores
    if score_count > 3:
        scores = scores[:3]
    else:
        scores = scores[1:]
    for score in scores:
        for letter in score[0]:
            data_to_write.append(ord(letter))
        data_to_write.append(score[1])
    eeprom.write_block(0,data_to_write)
    end_of_game = True

# Generate guess number
def generate_number():
    #print("generate_number...")
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    #print("btn_increase_pressed...")
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    global current_guess

    if value == None:
        print("No button actions until game begins")
    else:
        
        current_guess = 0 if current_guess == 7 else current_guess + 1
        LED1 = [1,3,5,7]
        LED2 = [2,3,6,7]

        if current_guess in LED1:
            GPIO.output(LED_value[0], GPIO.HIGH)
        else:
            GPIO.output(LED_value[0], GPIO.LOW)
        if current_guess in LED2:
            GPIO.output(LED_value[1], GPIO.HIGH)
        else:
            GPIO.output(LED_value[1], GPIO.LOW)
        if current_guess > 3:
            GPIO.output(LED_value[2], GPIO.HIGH)
        else:
            GPIO.output(LED_value[2], GPIO.LOW)

# Guess button
def btn_guess_pressed(channel):
    #print("btn_guess_pressed...")
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    global end_of_game, name, num_guesses

    if value == None:
        print("No button actions until game begins.")
    elif current_guess == -1:
        print("No value to guess yet. Use the other button to increase your guess.")
    else:
        start = time.time()
        while GPIO.input(btn_submit) == GPIO.LOW:
            pass
        length = time.time() - start
        if length > 2:
            pwm_buzzer.ChangeDutyCycle(0)
            pwm_LED.ChangeDutyCycle(0)
            for idx in range(3):
                GPIO.output(LED_value[idx], GPIO.LOW)
            GPIO.remove_event_detect(btn_submit)
            end_of_game = True
        else:
            num_guesses += 1
            delta = abs(value - current_guess)
            if delta != 0:
                accuracy_leds()
                trigger_buzzer()
            else:
                #win
                GPIO.remove_event_detect(btn_submit)
                pwm_buzzer.ChangeDutyCycle(0)
                pwm_LED.ChangeDutyCycle(0)
                for idx in range(3):
                    GPIO.output(LED_value[idx], GPIO.LOW)
                
                name = input("Correct! The secret number was " + str(value) + "!\nPlease enter your name (3 characters) for the scoreboard: ")
                while len(name) != 3:
                    name = input("Please enter a valid name (exactly 3 characters): ")
                save_scores() 

# LED Brightness
def accuracy_leds():
    #print("accuracy_leds...")
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    global pwm_LED

    brightness = current_guess/value*100 if current_guess < value else (8-current_guess)/(8-value)*100
    pwm_LED.ChangeDutyCycle(brightness)

# Sound Buzzer
def trigger_buzzer():
    #print("trigger_buzzer...")
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    global pwm_buzzer

    frequency = 1
    dutycycle = 0
    delta = abs(value - current_guess)
    if delta <=3 :
        if delta == 3:
            frequency = 1.5
        elif delta == 2:
            frequency = 2
        else:
            frequency = 4
        dutycycle = 50
    pwm_buzzer.ChangeFrequency(frequency)
    pwm_buzzer.ChangeDutyCycle(dutycycle)


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()        
        while True:
            menu()          
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
        pwm_LED.stop()
        pwm_buzzer.stop()