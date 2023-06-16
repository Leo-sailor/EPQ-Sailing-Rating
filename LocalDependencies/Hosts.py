import requests

from LocalDependencies.Main_core import Csvcode
import LocalDependencies.General as Base
from LocalDependencies.Csv_custom import Csvnew
import LocalDependencies.leo_dataclasses as dat
import datetime
from pickle import load as _load
from os import remove as _remove
from time import sleep as _sleep
from LocalDependencies.Imports import Import_manager


class HostScript:

    def __init__(self):
        self.inpmethod = ''
        self.inputmethodname = ''

    def torun(self,*args):
        global universecsv
        if len(args) >2:
            universecsv = Csvcode(args[1],args[2])
        else:
            universecsv = Csvcode()

        while True:
            Base.text_blocks(1)
            # TODO: add something for importing just sailors from a full file
            choice = Base.clean_input('\nWhat would you like to do?', 'i', rangelow=1, rangehigh=8)
            match choice:
                case 1:
                    event = self.import_event()
                    universecsv.add_event(event)
                case 2:
                    self.makenewsailor()
                case 3:
                    self.getsailorinfo()
                case 4:
                    break
                case 5:
                    self.sailorratingovertime()
                case 6:
                    print()
                    print(universecsv)
                    _sleep(0.5)
                case 7:
                    self.torun()
                    break
                case 8:
                    self.import_sailors()
    def import_sailors(self):
        imp_mgr = Import_manager()
        sailors = imp_mgr.import_sailors()
        print('The following {len(sailors)} sailors have been imported')
        for line in sailors:
            print(universecsv.getinfo(line,'all'))

    def sailorratingovertime(self):
        inpmethod = self.__getinputmethod()
        inp = Base.clean_input(f'(enter (_a) for all) \nPlease enter the sailor\'s {self.inputmethodname}:', 's')
        sailorid = universecsv.getsailorid(inpmethod, inp)
        # TODO make this work and finnish it

    def getsailorinfo(self):
        info_codes = {'c': 'Championship Number', 's': 'Sail Number', 'l': 'Light wind rating', 'm': 'Medium wind rating',
             'h': 'Heavy wind rating', 'n': 'Name', 'i': 'sailorid', 'o': 'Overall rating', 'r': 'Rank',
             'e': 'Total events', 'd': 'Date of last event', 'z': 'Zone/Region', 't': 'Territory/country', 'a': 'All',
             'S': 'Sailor info'}
        print('\nSAILOR INFO WIZZARD\n')
        print('please enter type of information you would like to recive')
        for key,val in info_codes.items(): # prints all the info_codes
            print(f'({key}) for {val}')

        outtype = Base.clean_input("\nWhat would u like to recive?", 's')
        outtype.lower().strip()
        outtypename = info_codes[outtype]

        inpmethod = self.__getinputmethod()
        inp = Base.clean_input(f'Please enter the sailor\'s {self.inputmethodname}:', 's')

        sailorid = universecsv.getsailorid(inpmethod,inp)
        out = universecsv.getinfo(sailorid, outtype)

        if outtype == 'd':
            twothousand = datetime.date(2000, 1, 1)
            out = twothousand + datetime.timedelta(days=float(out))

        print(f'\n{inp}\'s {outtypename} is {out}')

    @staticmethod
    def makenewsailor(name=None, sailno=None, champ=None,nat = None,fullspeed=False):

        print('\n NEW SAILOR WIZZARD')
        if name is None:
            name = Base.clean_input('Please enter the sailor\'s Full name: ', 's', charlevel=3)
        name = name.split(' ', 1)
        first = name[0]
        try:
            sur = name[1]
        except IndexError:
            sur = Base.clean_input('Please enter the sailor\'s  surname: ', 's', charlevel=3)
        if champ is None:
            champ = str(Base.clean_input('Please enter the sailor\'s Championship number '
                                        '\n(Please enter (000) if the sailor does not have a Champ number): ',
                                        'i', rangehigh=999))
        else:
            champ = str(champ)
        if sailno is None:
            sailno = str(Base.clean_input('Please enter the sailor\'s Sail number '
                                         '\n(Please ignore any letters):',
                                         'i', rangehigh=99999))
        else:
            sailno = str(sailno)
        if nat is None:
            nat = Base.clean_input('\n(enter) for automatic\nPlease enter the sailor\'s 3 letter country code:', 's', charlevel=3).upper()[:3]
        nat = str(nat)
        out = Base.generate_sailor_id(nat, sailno, first, sur)
        sailorid = out[0]
        nat = out[1]
        if nat == 'GBR' and not(fullspeed):
            region = Base.clean_input('\n SC - Scotland\n SE - London and South-east\n SW - South-west\n SO - South'
                                     '\n MD - Midlands\n NO - North\n NI - Northen Ireland\n WL - Wales\n EA - East'
                                     '\n NA - Unknown\nPlease enter {} {}\'s\'s 2 letter RYA region code:'.format(first, sur),
                                     's', charlevel=3).upper()[:2]
            if region not in ['SC', 'SE', 'SW', 'SO','MD','NO','NI','WL','EA']:
                region = 'NA'
        else:
            region = 'NA'
        return universecsv.addsailor(sailorid, first, sur, champ, sailno, region, nat)

    def addeventlazy(self):
        inp = 2
        light_race_num = 0
        med = 0
        heavy = 0
        while inp != 1:
            racenum = Base.clean_input('\nPlease enter the number of races in the event (1-20):', 'i', rangelow=1,
                                       rangehigh=20)
            light_race_num = Base.clean_input(
                '\nPlease enter the number of light wind (0-8kts) races in the event (0-{}):'.format(racenum), 'i',
                rangehigh=racenum)
            racenum -= light_race_num
            med = Base.clean_input(
                'Please enter the number of medium wind (9-16kts) races in the event (0-{}):'.format(racenum), 'i',
                rangehigh=racenum)
            racenum -= med
            heavy = racenum
            inp = Base.clean_input(f'\nThat means there were\n{light_race_num} light wind races\n{med} medium wind races\n{heavy} strong wind races\n'
                                  f'press (1) to confirm or press (2) to try again:', 'i',
                                   1, rangehigh=2)

        days = Base.clean_input('\nHow many days ago was the final race of the event(0-500):', 'i')
        event = dat.Event([], days)
        results_obj = self.__getranking('the event')

        for _ in range(light_race_num):
            event.append(dat.Race(results_obj, 1, days))
        for _ in range(med):
            event.append(dat.Race(results_obj, 2, days))
        for _ in range(heavy):
            event.append(dat.Race(results_obj, 3, days))
        return event

    def addeventproper(self):
        racenum = Base.clean_input('\nPlease enter the number of races in the event (1-20):', 'i', rangelow=1, rangehigh=20)
        days = Base.clean_input('\nHow many days ago was the final race of the event(0-500):', 'i')
        event = dat.Event([], days)
        for x in range(racenum):
            racetext = ' '.join(['Race', str(x+1)])
            print(f'\n{racetext.upper()} ENTRY WIZZARD')
            wind = Base.clean_input(f'\nPlease enter the wind strength for {racetext}\n'
                                   f'(1) for light wind - 0-8kts\n'
                                   f'(2) for medium wind - 9-16kts\n'
                                   f'(3) for strong wind - 17+ kts:', 'i', rangehigh=3, rangelow=1)
            info = self.__getranking(racetext)
            event.append(dat.Race(info, wind, days))
        return event

    def addeventcsv(self):
        racenum = Base.clean_input('\nPlease enter the number of races in the event (1-20):', 'i', rangelow=1,
                                   rangehigh=20)
        days = Base.clean_input('\nHow many days ago was the final race of the event(0-500):', 'i')
        event = dat.Event([],days)
        for x in range(racenum):
            racetext = ' '.join(['Race', str(x + 1)])
            print(f'\n{racetext.upper()} ENTRY WIZZARD')
            fileloc = Base.clean_input(f'Please enter the full file location of the file for {racetext}:', 's')
            currfile = Csvnew(fileloc)
            wind = int(currfile.getcell(0, 1))

            currsailorids = currfile.getcolumn(0, excudedrows= [0, 1])
            positions = [int(x) for x in currfile.getcolumn(1, excudedrows= [0, 1])]
            results_obj = dat.Results(currsailorids,positions)
            event.append(dat.Race(results_obj, wind, days))
        return event

    def __getranking(self, eventname: str) -> dat.Results:
        self.__getinputmethod()
        working = True
        position = 0
        positions = []
        sailorids = []
        rawinps = []
        speedprint = []
        print("\nPlease do not include sailors that DNC but all other codes"
              "\nPress (d) when you are done\n"
              "Press (b) if you want to remove the last sailor\n")
        while working:
            if speedprint != []:
                print("\nPosition:    {}:    Sailor-id:".format(self.inputmethodname))
                toprint = '\n'.join(speedprint)
                print(toprint)
            position += 1
            inp = Base.clean_input(
                "\nPlease enter the {} of {} place in {}:".format(self.inputmethodname, Base.ordinal(position),
                                                                  eventname), 's').lower()
            if inp == 'd':
                working = False
            elif inp == 'b':
                position -= 1
                positions.pop(-1)
                speedprint.pop(-1)
                sailorids.pop(-1)
                rawinps.pop(-1)
            else:
                inp.lower().strip()
                sailor = universecsv.getsailorid(self.inpmethod, inp)
                if sailor in sailorids:
                    print('\nThis sailor has already been entered, please try again')
                    position -= 1
                else:
                    sailorids.append(sailor)
                    positions.append(position)
                    rawinps.append(inp)
                    speedprint.append(f'{position}            {inp}           {sailor}')
        return dat.Results(sailorids, positions)

    def __getinputmethod(self):
        print('\n INPUT METHOD SELECTION')
        inpmethods = ['c', 'n', 'i', 's']
        if self.inpmethod in inpmethods:
            if self.inpmethod == 'c':
                self.inputmethodname = 'Championship Number'
            elif self.inpmethod == 'n':
                self.inputmethodname = 'Name'
            elif self.inpmethod == 'i':
                self.inputmethodname = 'Sailor-id'
            else:
                self.inputmethodname = 'Sail Number'
            inp = Base.clean_input((''.join(('\nYour current selected input method is: ', self.inputmethodname,
                                            '\nWould you like to change it?\n(0) for no\n(1) for yes:'))), 'i',
                                   rangehigh=1)
            if inp == 1:
                ip = ''
            else:
                ip = self.inpmethod
        else:
            ip = ''
        while ip not in inpmethods:
            ip = Base.clean_input('\nHow would you like to enter sailors information?\n'
                                 '(c) for Championship Number\n'
                                 '(i) for Sailor-id\n'
                                 '(n) for Name\n'
                                 '(s) for Sail Number:', 's').lower()
        self.inpmethod = ip
        if self.inpmethod == 'c':
            self.inputmethodname = 'Championship Number'
        elif self.inpmethod == 'n':
            self.inputmethodname = 'Name'
        elif self.inpmethod == 'i':
            self.inputmethodname = 'Sailor-id'
        else:
            self.inputmethodname = 'Sail Number'
        return ip

    def import_pickled_event(self):
        fileloc = '_________'
        while fileloc[-6:] != '.event':
            if fileloc != '_________':
                print('that file is not of the correct type, please try again')
            fileloc = Base.getfilename()
        with open(fileloc, 'rb') as f:
            event = _load(f)
        return event

    def import_event(self):
        if not universecsv.admin:
            print('\nTo add an event you need admin rights')
            if not universecsv.adminrights():
                print('\nAdd event failed, please try with admin rights')
                return None

        print("\nEVENT ENTRY WIZZARD")
        inp = Base.clean_input('\n(1) for entering overall event results (less accurate - quicker)\n'
                               '(2) for entering individual race results (higher accuracy - slower)\n'
                               '(3) for importing previous race csv (needs previously entered csv)\n'
                               '(4) for importing an online results file (needs internet - html/htm/pdf)\n'
                               '(5) for importing an local file (html/htm/pdf)\n'
                               '(6) for importing a .event file\n'
                               '(0) to cancel\n',
                               'i', rangehigh=5, rangelow=0)
        match inp:
            case 1:
                event = self.addeventlazy()
            case 2:
                event = self.addeventproper()
            case 3:
                event = self.addeventcsv()
            case 4:
                event = self.add_online_event() #
            case 5:
                event = self.addeventlocal()
            case 6:
                event = self.import_pickled_event()
            case _:
                return None
        return event

    def addeventlocal(self,file:str = None) -> dat.Event:
        inp_mgr = Import_manager('F')
        return inp_mgr.to_event(universecsv)

    def add_online_event(self) -> dat.Event:
        inp_mgr = Import_manager('L')
        return inp_mgr.to_event(universecsv)


def main():
    HostScript.torun()

if __name__ == '__main__':
    main()

