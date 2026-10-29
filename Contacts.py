from SmartConsole import *

class Contacts:
    def __init__(self):
        info = "Manage you contacts usin this app"
        color = "GREY"
        version = 0.1
        self.sc = SmartConsole("Contact manager", version, info, color, "640x640")
        self.sc.add_main_menu_item("DISPLAY CONTACTS", self.display_contacts)
        self.sc.add_main_menu_item("NEW CONTACT", self.add_new_contact)
        self.sc.add_main_menu_item("EDIT CONTACT", self.add_edit_contact)
        self.sc.add_main_menu_item("DELETE CONTACT", self.add_delete_contact)
        self.sc.add_main_menu_item("IMPORT CONTACTS", self.import_contacts)
        self.sc.add_main_menu_item("EDIT DATABASE STRUCTURE", self.edit_database_structure)
        self.sc.add_settings_key("Contacts location")
        self.sc.display_main_menu()

    # region DISPLAY
    def display_contacts(self):
        # set status lbl
        self.sc.set_status_label("DISPLAY CONTACTS")

        # load database
        if not self.load_database():
            self.sc.restart()
            return

        # generate html
        html = []

        # Title
        html.append("<html>")
        html.append("<head>")
        html.append("<title>My Contacts List</title>")
        html.append("""
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
        """)
        html.append("</head>")
        html.append("<body>")

        html.append("<h1>My Contacts List</h1>")

        # Table
        html.append("<table>")

        # Header row
        html.append("<tr>")
        for col in self.DB_STRUCTURE:
            html.append(f"<th>{col[0]}</th>")
        html.append("</tr>")

        # Data rows
        for key, val in self.DB.items():
            html.append("<tr>")

            # First column = key
            html.append(f"<td>{key}</td>")

            # Remaining columns = values from list
            for item in val:
                html.append(f"<td>{item}</td>")

            html.append("</tr>")

        html.append("</table>")
        html.append("</body>")
        html.append("</html>")

        with open("contacts.html", "w", encoding="utf-8") as f:
            f.write("\n".join(html))

        # open HTML
        self.sc.open("contacts.html")

        # restart
        self.sc.restart()
    
    # endregion
    # region ADD
    def add_new_contact(self):
        # set status lbl
        self.sc.set_status_label("NEW CONTACT")

        # load database
        if not self.load_database():
            self.sc.restart()
            return

        # get data
        new_line = []

        for key, keytype in self.DB_STRUCTURE:
            data_validated = False
            first = True
            while not data_validated:
                # get data
                data = self.sc.input("Insert "+key+" ["+keytype+"]")
                data_validated = self.validate_data(data, keytype)

                # validate data
                if first:
                    if data in self.DB:
                        self.sc.print("The first data item must be unique. "+data+" already exists")
                        data_validated = False
                    else:
                        first = False

            new_line.append(data)
        
        # add new line to database
        self.DB[new_line[0]] = new_line[1:]

        # save database
        self.save_database()
        
        # restart
        self.sc.restart()

    def validate_data(self, data, datatype):
        if datatype == "NUMBER":
            try:
                data = int(data)
                return True
            except:
                self.sc.print("Invalid data type! NUMBER Expected")
                return False

        if datatype == "BOOL":
            if data.upper() == "Y" or data.upper() == "N":
                return True
            else:
                self.sc.print("Invalid data type! [Y/N] Expected")
                return False
        return True
    
    # endregion
    # region EDIT
    def add_edit_contact(self):
        # set status lbl
        self.sc.set_status_label("EDIT CONTACT")

        # load database
        if not self.load_database():
            self.sc.restart()
            return

        # get pk
        pk = self.get_pk()

        # choose data to edit
        options = [x[0] for x in self.DB_STRUCTURE[1:]]
        data_to_edit = self.sc.choose("Choose what data you want to edit", options)
        index_of_data_to_edit = options.index(data_to_edit)

        # edit choice
        data_validated = False

        # validate new data
        datatype = self.DB_STRUCTURE[index_of_data_to_edit+1][1]
        
        while not data_validated:
            new_data = self.sc.input("Current "+data_to_edit+": "+self.DB[pk][index_of_data_to_edit]+"\nInsert new "+data_to_edit)
            data_validated = self.validate_data(new_data, datatype)

        # update database
        self.DB[pk][index_of_data_to_edit] = new_data
        
        # save new data
        self.save_database()
        
        # restart
        self.sc.restart()

    def get_pk(self):
        # get pk
        good_pk = False
        while not good_pk:
            good_pk = True
            pk = self.sc.input("Insert contact "+self.DB_STRUCTURE[0][0])
            if self.DB_STRUCTURE[0][1] == 'NUMBER':
                try:
                    number = int(pk)
                except:
                    good_pk = False
                    self.sc.print("Error! "+self.DB_STRUCTURE[0][0]+" is set to must be a NUMBER")
            if not pk in self.DB:
                good_pk = False
                self.sc.print("Error! There is no such "+self.DB_STRUCTURE[0][0]+" in the database")
        return pk
    
    # endregion
    # region DELETE
    def add_delete_contact(self):
        # set status lbl
        self.sc.set_status_label("DELETE CONTACT")

        # load database
        if not self.load_database():
            self.sc.restart()
            return

        # get pk
        pk = self.get_pk()

        # question if you want to delete
        data = ""
        i = 0
        data += self.DB_STRUCTURE[i][0]+": "+pk+"\n"
        i += 1
        for val in self.DB[pk]:
            data += self.DB_STRUCTURE[i][0]+": "+val+"\n"
            i += 1
        if self.sc.question(data+"\nAre you sure you want to delete the contact?"):
            del self.DB[pk]
        
        # save new data
        self.save_database()

        # restart
        self.sc.restart()
    
    # endregion
    # region IMPORT
    def import_contacts(self):
        # set status lbl
        self.sc.set_status_label("IMPORT CONTACTS")

        # load database
        if not self.load_database():
            self.sc.restart()
            return

        # get file
        filepath = self.sc.input("Insert path to import file")

        # read file
        if self.sc.test_paths((filepath,)):
            file = open(filepath, 'r')
            lines = file.readlines()
            file.close()

            ln = 0
            for line in lines:
                ln += 1 
                line = line.replace("\n","").upper().split(",")
                if len(line) != len(self.DB_STRUCTURE):
                    self.sc.print("Error in line: "+str(ln)+"\n\nExpected data structure:\n"+str(self.DB_STRUCTURE)+"\n\nGiven data:\n"+str(line))
                    break
                i = 0
                unique = True
                pk = ""
                for item in line:
                    if not self.validate_data(item, self.DB_STRUCTURE[i][1]):
                        self.sc.print("Error in line: "+str(ln)+"\n\nExpected data structure:\n"+str(self.DB_STRUCTURE[i][1])+"\n\nGiven data:\n"+str(item))
                        break
                    if unique:
                        if item in self.DB:
                            self.sc.print("Error in line: "+str(ln)+"\n\n"+item+" Aleardy exists!")
                            break
                        else:
                            self.DB[item] = []
                            pk = item
                            unique = False
                    else:
                        self.DB[pk].append(item)
                    i += 1
        
        # save new data
        self.save_database()

        # restart
        self.sc.restart()
    
    # endregion
    # region SAVE
    def save_database(self):
        with open(self.DBFILE, "w", encoding="utf-8") as file:
            header_csv = ",".join(item[0] for item in self.DB_STRUCTURE)
            file.write(header_csv + "\n")

            for key, val in self.DB.items():
                row = [key] + val
                file.write(",".join(map(str, row)).upper() + "\n")

    # endregion
    # region LOAD
    def load_database(self):
        # read db structure
        self.DB = {}
        self.DB_STRUCTURE = []
        self.DBFILE = self.sc.get_settings_value("Contacts location")+"/contacts.csv"

        if self.sc.test_paths(("database_structure.txt",)):
            file = open("database_structure.txt", 'r')
            lines = file.readlines()
            file.close()

            for line in lines:
                line = line.replace("\n","").upper()
                line = line.split(" ")
                if len(line) > 1:
                    colname = line[0]
                    coltype = line[1]
                    self.DB_STRUCTURE.append((colname,coltype))

            # create contacts list if not exists
            if not os.path.isfile(self.DBFILE):
                file = open(self.DBFILE, 'w')
                text = ""
                for col in self.DB_STRUCTURE:
                    text += col[0]+","
                text = text[0:-1]
                file.write(text+"\n")
                file.close()

            # load contacts
            file = open(self.DBFILE, 'r')
            lines = file.readlines()
            file.close()

            line_len = len(self.DB_STRUCTURE)
            ln = 1
            for line in lines[1:]:
                ln += 1
                line = line.replace("\n","").upper()
                line = line.split(",")
                if line_len == len(line):
                    if not self.validate_data(line[0],self.DB_STRUCTURE[0][1]):
                        self.sc.print("Error in line: "+str(ln)+"\n\nExpected data structure:\n"+str(self.DB_STRUCTURE[0][1])+"\n\nGiven data:\n"+str(line[0]))
                        return False
                    if not line[0] in self.DB:
                        self.DB[line[0]] = []
                    else:
                        self.sc.print("Error in line: "+str(ln)+"\n\n"+line[0]+" Aleardy exists!")
                        return False
                    i = 0
                    for val in line[1:]:
                        i += 1
                        if self.validate_data(val,self.DB_STRUCTURE[i][1]):
                            self.DB[line[0]].append(val)
                        else:
                            self.sc.print("Error in line: "+str(ln)+"\n\nExpected data structure:\n"+str(self.DB_STRUCTURE[i][1])+"\n\nGiven data:\n"+str(val))
                            return False
                else:
                    self.sc.print("Error in file:\n"+self.DBFILE+"\n\nIn line "+str(ln)+": Invalid structure\n\nGiven structure:\n"+str(line)+"\n\nExpected structure:\n"+str(self.DB_STRUCTURE))
                    return False
        else:
            return False

        return True

    def edit_database_structure(self):
        self.sc.open("database_structure.txt")
        
        # restart
        self.sc.restart()
Contacts()