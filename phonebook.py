import mysql.connector
import PySimpleGUI as sg
from mysql.connector import Error

sg.theme("DarkBrown1")

def execute_query(connection, query):
    """ Function for executing queries """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_read_query(connection, query):
    """ Function for selecting records """
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

def create_connection(host_name, user_name, user_password, db_name):
    """ Connects to the database """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

connection = create_connection("localhost", "root", "", "phonebook")

def insert_person(name: str, age: int, phoneNumber: int, phoneBrand: str, connection):
    """ Function for inserting a person into the phonebook """
    try:
        data = fetch_data(connection)
        for person in data:
            person = person[1:len(person)]
            newPerson = (name, int(age), int(phoneNumber), phoneBrand)
            if person == newPerson:
                return False
    except ValueError:
        return False

    create_person = """
    INSERT INTO 
        `names` (`name`, `age`, `number`, `phoneBrand`)
    VALUES
        ('"""+name+"""', '"""+str(age)+"""', '"""+str(phoneNumber)+"""', '"""+phoneBrand+"""');
    """
    execute_query(connection, create_person)
    return True

def delete_person(id: int, connection):
    """ Function for deleting a person from the phonebook """
    try:
        data = fetch_data(connection) # return a list of tuples with all the data. The ID is in index 0
        for person in data:
            if int(person[0]) == int(id):
                delete_person = f"DELETE FROM names WHERE id = {id}"
                execute_query(connection, delete_person)
                return True
            else:
                pass
        return False
    except ValueError:
        pass # :)

def person_exists(id, connection):
    try:
        data = fetch_data(connection)
        for person in data:
            if int(person[0]) == int(id):
                return True
            else:
                pass
        return False
    except ValueError:
        return False

def update_person(id, name, age, phonenum, phonebrand, connection):
    """ Function for editing an entry """
    update_entry = """
    UPDATE 
        names
    SET 
        name = '"""+str(name)+"""',
        age = '"""+str(age)+"""',
        number = '"""+str(phonenum)+"""' ,
        phoneBrand = '"""+str(phonebrand)+"""'
    WHERE id = """+str(id)+"""
    """
    execute_query(connection, update_entry)

def get_phones(connection):
    data = fetch_data(connection)
    phones = ["None"]
    for phone in data:
        # 4 is the column with phones
        if phone[4] in phones:
            continue
        else:
            phones.append(phone[4])
    return phones

def filter_phones(phone, connection):
    data = fetch_data(connection)
    filteredPhones = []
    for entry in data:
        # 4 is the column with phones
        if entry[4] == phone:
            filteredPhones.append(entry)
    return filteredPhones


# table with all the information for each person
create_names_table = """
CREATE TABLE IF NOT EXISTS names (
    id int auto_increment,
    name TEXT NOT NULL,
    age INT,
    phoneNumber INT,
    phoneBrand TEXT,
    PRIMARY KEY (id)
) ENGINE = InnoDB
"""
execute_query(connection, create_names_table) # calls execute_query to create table in database

def fetch_data(connection):
    select_people = "SELECT * FROM names"
    fetched_phonebook_data = execute_read_query(connection, select_people)
    return fetched_phonebook_data
fetch_data(connection)
headings = ["ID", "Name", "Age", "Phonenumber", "Phonebrand"]

# create our window
tab_1 = [[sg.Text("Name", size=(15,1)), sg.Input('', key='name', size=(35,1))],
        [sg.Text("Age", size=(15,1)), sg.Input('', key='age', size=(35,1))],
        [sg.Text("phone number", size=(15,1)), sg.Input('', key='phonenum', size=(35,1))],
        [sg.Text("phone brand", size=(15,1)), sg.Input('', key='phonebrand', size=(35,1))],
        [sg.Button('Submit')],
        [sg.Text("", key="-CONFIRM_INSERTION-")]]

phones = get_phones(connection) # function returns a list of all the phones in the database
tab_2 = [[sg.OptionMenu(values=phones, default_value="Filter phones", size=(10,1), key="-FILTER-"), sg.Button("Filter")],
        [sg.Table(
            values=fetch_data(connection),
            headings=headings,
            auto_size_columns=True,
            justification='right',
            key='-TABLE-',
            row_height=30
            )],
            [sg.Text("Deletion by id")],
            [sg.Input("", key="-PERSON_TO_DELETE-"), sg.Button("Delete")],
            [sg.Text("", key="-CONFIRM_DELETION-")],
            [sg.Text("Pick person to edit (ID)"), sg.Text("", key="-EDIT_ERROR_TEXT-")],
            [sg.Input("", key="-ID_TO_EDIT-"), sg.Button("Edit")],
            [sg.Text("Name", key="-TEXT1-", visible=False), sg.Input("", key="-1-", visible=False)],
            [sg.Text("Age", key="-TEXT2-", visible=False), sg.Input("", key="-2-", visible=False)],
            [sg.Text("Phonenumber", key="-TEXT3-", visible=False), sg.Input("", key="-3-", visible=False)],
            [sg.Text("Phonebrand", key="-TEXT4-", visible=False), sg.Input("", key="-4-", visible=False)],
            [sg.Button("Submit edit", visible=False, key="-CONFIRM_EDIT-"), sg.Text("", key="-EDIT_TEXT-", visible=False)]
            ]

layout = [[sg.TabGroup([[sg.Tab("Insert people", tab_1), sg.Tab("Overview", tab_2)]])]]

title = "Phonebook"
window = sg.Window(title, layout) # create window object
while True: # window event loop
    event, values = window.read() # open window
    if event == sg.WIN_CLOSED:
        break
    
    if event == "Submit": # if user clicks submit button
        if insert_person(
        values["name"],
        values["age"],
        values["phonenum"],
        values["phonebrand"],
        connection
        ):
            window['-TABLE-'].update(fetch_data(connection))
            window["-CONFIRM_INSERTION-"].update("Person inserted successfully!", text_color="green")
            window["name"].update("")
            window["age"].update("")
            window["phonenum"].update("")
            window["phonebrand"].update("")
            window["-FILTER-"].update(values=get_phones(connection))
        else:
            window["-CONFIRM_INSERTION-"].update("Person already exists in the database or invalid data!", text_color="red")

    if event == "Delete": # if user clicks delete button
        person = values["-PERSON_TO_DELETE-"]
        if delete_person(person, connection): # checks if its an actual entry in the database
            window["-TABLE-"].update(fetch_data(connection))
            window["-CONFIRM_DELETION-"].update("Person deleted", text_color="green")
            window["-FILTER-"].update(values=get_phones(connection))
        else:
            window["-CONFIRM_DELETION-"].update("Not a valid ID dumbass", text_color="red")

    if event == "Edit": # if user clicks edit button
        person = values["-ID_TO_EDIT-"]
        data = fetch_data(connection)
        try:
            for entry in data:
                if int(entry[0]) == int(person):
                    id = entry[0]
                    oldName = entry[1]
                    oldAge = entry[2]
                    oldPhonenum = entry[3]
                    oldBrand = entry[4]
                    window["-EDIT_ERROR_TEXT-"].update("")
                else:
                    continue
        except ValueError:
            window["-EDIT_ERROR_TEXT-"].update("Invalid ID!", text_color="red")

        if person_exists(person, connection): # checks if its an actual entry in the database
            window["-1-"].update(f"{oldName}", visible=True)
            window["-2-"].update(f"{oldAge}", visible=True)
            window["-3-"].update(f"{oldPhonenum}", visible=True)
            window["-4-"].update(f"{oldBrand}", visible=True)
            window["-TEXT1-"].update(visible=True)
            window["-TEXT2-"].update(visible=True)
            window["-TEXT3-"].update(visible=True)
            window["-TEXT4-"].update(visible=True)
            window["-CONFIRM_EDIT-"].update(visible=True)
        else:
            window["-EDIT_ERROR_TEXT-"].update("Invalid ID!", text_color="red")

    if event == "-CONFIRM_EDIT-":
        newName = values["-1-"]
        newAge = values["-2-"]
        newPhonenum = values["-3-"]
        newBrand = values["-4-"]
        update_person(id, newName, newAge, newPhonenum, newBrand, connection)
        window["-TABLE-"].update(fetch_data(connection))
        window["-EDIT_TEXT-"].update("Person edited!", text_color="green", visible=True)
        window["-FILTER-"].update(values=get_phones(connection))

    if event == "Filter":
        phone = values["-FILTER-"]
        if phone == "None":
            window["-TABLE-"].update(fetch_data(connection))
        elif phone == "Filter phones": # This is the default_value
            pass
        else:
            filteredByPhones = filter_phones(phone, connection)
            window["-TABLE-"].update(filteredByPhones) 


# TODO
# person_exists() function, this code is so fucking garbage it's unbelievable but it works so i have a really hard time caring :)
# the exception handling is shit, too lazy though cause it works and i dont care
# Make it look pretty :3 (most likely wont ever happen because SNOREEEEE) 
# delete and edit users based on highlights and not id, pretty easy but lazy
