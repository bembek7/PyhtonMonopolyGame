from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QApplication
from PySide2 import QtCore
from Property import TypicalProperty
from ui_GameWindow import Ui_MainWindow
from Field import PropertyField


class MainWindow(QMainWindow):
    """
    MainWindow is the main class representing the game board and containing most of the logic for the game.
    It sets up the GUI and connects the buttons to their respective actions.

    Attributes
    ----------
    ui (Ui_MainWindow): Instance of the ui form.
    used_names (list): List of names of players that have already been used.
    game_instance (Game): Game instance
    board (Board): board instance
    nr_of_rounds (int): Number of rounds in game.
    curr_player_index (int): Index of current player in game
    already_rolled (bool): keep track whether current player already roll or not

    Methods
    -------
    __init__(game: Game, parent=None):
        initializes the MainWindow class and sets up the GUI, connects buttons to their respective actions and initializes attributes
    check_broke():
        checks if player is brokw
    check_jail():
        checks if player is in jail and sets up gui depending on it
    add_player():
        adds a player to the game
    clicked_play():
        call functions connected with startting the game
    rolled():
        call functions that need to be called after player rolled the dice
    end_turn():
        call functions that need to be called with the end of the turn
    player_buys():
        allows the current player to buy the property they landed on
    deactivating_property():
        updates gui when player deactivates property and call function to deactivate it
    activating_property():
        updates gui when player activates property and call function to activate it
    buying_apartment():
        updates gui when player buys apartment and call function to buy it
    selling_apartment():
        updates gui when player sells apartment and call function to sell it
    selling_property():
        updates gui when player sells property and call function to sell it
    perform_field_action():
        performs action on a field
    player_win():
        changes for winner screen
    player_gave_up():
        updates the interface when player gave up
    free_of_jail():
        updates the interface when player leaves jail
    set_names():
        set names of all the properties on the board
    set_prices():
        set prices of all the properties on the board
    set_properties():
        sets all the properties on the board
    update_sell_button():
        enable or disable sell button depending on conditions
    update_player_list():
        update list of players in the game
    show_player():
        displays information about the player who is currently selected
    update_activate_property():
        update the status of activate property button update the status of buy apartment button depending on certain conditions
    update_buy_apartment():
        update the status of buy apartment button depending on certain conditions
    turn():
        performes actions on the beginning of the turn
    remove_player_from_board(player):
        removes a player from the board
    other are obvious
    """
    def __init__(self, game, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.plansze.setCurrentIndex(0)
        self.ui.DodajGraczaButton.clicked.connect(self.add_player)
        self.ui.GrajButton.clicked.connect(self.clicked_play)
        self.ui.RzutButton.clicked.connect(self.rolled)
        self.ui.KoniecTuryButton.clicked.connect(self.end_turn)
        self.ui.KupButton.clicked.connect(self.player_buys)
        self.ui.ZastawButton.clicked.connect(self.deactivating_property)
        self.ui.WykupButton.clicked.connect(self.activating_property)
        self.ui.KupDomekButton.clicked.connect(self.buying_apartment)
        self.ui.SprzedajDomekButton.clicked.connect(self.selling_apartment)
        self.ui.SprzedazButton.clicked.connect(self.selling_property)
        self.ui.PoddajButton.clicked.connect(self.player_gave_up)
        self.ui.WiezienieButton.clicked.connect(self.free_of_jail)
        self.ui.ZastawButton.setEnabled(False)
        self.ui.GrajButton.setEnabled(False)
        self._used_names = []
        self._game_instance = game
        self._board = self._game_instance.board
        self._nr_of_rounds = 0
        self._curr_player_index = 0
        self.ui.ListaGraczyGra.itemClicked.connect(self.show_player)
        self.ui.ListaKomu.itemClicked.connect(self.update_sell_button)
        self.ui.ListaNaSprzedaz.itemClicked.connect(self.update_sell_button)
        self.ui.ListaWykup.itemClicked.connect(self.update_activate_property)
        self.ui.ListaKupienia.itemClicked.connect(self.update_buy_apartment)
        self.ui.Kwota.valueChanged.connect(self.update_sell_button)
        self._already_rolled = False
        self.set_names()
        self.set_prices()
        self.set_properties()

    def check_jail(self):
        if self._curr_player.is_in_jail():
            self.ui.Wykuptury.setText(str(self._curr_player.get_rounds_left()))
        else:
            self.ui.Wykuptury.setText("")

    def check_broke(self):
        if self._curr_player.is_broke():
            self.ui.Broke.setText("Nie możesz skończyć tury, mając długi!")
            self.ui.KoniecTuryButton.setEnabled(False)
            self.ui.RzutButton.setEnabled(False)
        else:
            self.ui.Broke.setText("")
            self.ui.RzutButton.setEnabled(not (self._already_rolled or self._curr_player.is_in_jail()))
            self.ui.KoniecTuryButton.setEnabled(self._already_rolled or self._curr_player.is_in_jail())

    def player_gave_up(self):
        self.remove_player_from_board(self._curr_player)
        self._used_names.remove(self._curr_player.get_name())
        self._game_instance.player_loses(self._curr_player)
        self.update_player_list()
        self._curr_player_index -= 1
        self.end_turn()

    def player_win(self, player_name):
        self.ui.Win.setText(f"Wygrywa gracz: {player_name}")
        self.ui.plansze.setCurrentIndex(2)

    def update_sell_button(self):
        if self.ui.ListaNaSprzedaz.currentItem() is not None and self.ui.ListaKomu.currentItem() is not None and self.ui.Kwota.value() > 0:
            self.ui.SprzedazButton.setEnabled(True)
        else:
            self.ui.SprzedazButton.setEnabled(False)

    def selling_property(self):
        self._game_instance.sell_property(self._curr_player, self.ui.Kwota.value(), self.ui.ListaNaSprzedaz.currentItem().text(), self.ui.ListaKomu.currentItem().text())
        self.ui.Kwota.setValue(0)
        self.update_lists()

    def update_properties_selling(self):
        self.ui.ListaNaSprzedaz.clear()
        for property in self._curr_player.get_sellable_properties():
            self.ui.ListaNaSprzedaz.addItem(str(property))

    def update_players_selling(self):
        self.ui.ListaKomu.clear()
        for player in self._game_instance.players:
            if player.get_name() != self._curr_player.get_name():
                self.ui.ListaKomu.addItem(player.get_name())

    def selling_apartment(self):
        if self.ui.ListaSprzedania.currentItem() is not None:
            property_name = self.ui.ListaSprzedania.currentItem().text()
            for field in self._board:
                if isinstance(field, PropertyField):
                    property = field.get_property()
                    if isinstance(property, TypicalProperty):
                        if property.get_name() == property_name:
                            self._curr_player.sell_apartment(property)
                            self.update_lists()
                            break

    def buying_apartment(self):
        if self.ui.ListaKupienia.currentItem() is not None:
            property_name = self.ui.ListaKupienia.currentItem().text()
            for field in self._board:
                if isinstance(field, PropertyField):
                    property = field.get_property()
                    if isinstance(property, TypicalProperty) and property.get_name() == property_name:
                        self._curr_player.buy_apartment(property)
                        self.update_lists()
                        break

    def deactivating_property(self):
        if self.ui.ListaZastaw.currentItem() is not None:
            property_name = self.ui.ListaZastaw.currentItem().text()
            for field in self._board:
                if isinstance(field, PropertyField):
                    property = field.get_property()
                    if property.get_name() == property_name:
                        self._curr_player.deactivate_property(property)
                        self.update_lists()
                        break

    def activating_property(self):
        if self.ui.ListaWykup.currentItem() is not None:
            property_name = self.ui.ListaWykup.currentItem().text()
            for field in self._board:
                if isinstance(field, PropertyField):
                    property = field.get_property()
                    if property.get_name() == property_name:
                        self._curr_player.activate_property(property)
                        self.update_lists()
                        break

    def update_player_list(self):
        self.ui.ListaGraczyGra.clear()
        for name in self._used_names:
            self.ui.ListaGraczyGra.addItem(name)

    def show_list_widget(self, list_widget, properties, button):
        list_widget.clear()
        for property in properties:
            list_widget.addItem(property.get_name())
        button.setEnabled(len(properties) > 0)

    def update_buy(self):
        if self._board[self._curr_player.get_position()].can_buy(self._curr_player) and not self.already_buyed and self._already_rolled:
            self.ui.KupButton.setEnabled(True)
        else:
            self.ui.KupButton.setEnabled(False)

    def update_buy_apartment(self):
        if not self._curr_player.can_afford(self._game_instance.get_apartment_price_from_name(self.ui.ListaKupienia.currentItem().text())):
            self.ui.KupDomekButton.setEnabled(False)
        else:
            self.ui.KupDomekButton.setEnabled(True)

    def update_buy_out_of_jail(self):
        if self._curr_player.can_afford(self._game_instance.get_jail_price()) and self._curr_player.is_in_jail():
            self.ui.WiezienieButton.setEnabled(True)
        else:
            self.ui.WiezienieButton.setEnabled(False)

    def update_activate_property(self):
        if not self._curr_player.can_afford(self._game_instance.get_activation_price_from_name(self.ui.ListaWykup.currentItem().text())):
            self.ui.WykupButton.setEnabled(False)
        else:
            self.ui.WykupButton.setEnabled(True)

    def update_buying_buttons(self):
        self.update_buy()
        if self.ui.ListaKupienia.currentItem() is not None:
            self.update_buy_apartment()
        self.update_buy_out_of_jail()
        if self.ui.ListaWykup.currentItem() is not None:
            self.update_activate_property()

    def update_lists(self):
        self.show_deactivable_properties()
        self.show_activable_properties()
        self.show_available_apartments()
        self.show_sellable_apartments()
        self.set_properties()
        self.update_players_selling()
        self.update_properties_selling()
        self.update_sell_button()
        self.show_player(self.ui.ListaGraczyGra.currentItem())
        if self._already_rolled:
            self.ui.KupDomekButton.setEnabled(False)
        self.update_buying_buttons()
        self.check_jail()
        self.check_broke()

    def show_sellable_apartments(self):
        self.show_list_widget(self.ui.ListaSprzedania, self._curr_player.get_sellable_apartments(), self.ui.SprzedajDomekButton)

    def show_available_apartments(self):
        self.show_list_widget(self.ui.ListaKupienia, self._curr_player.get_available_apartments(), self.ui.KupDomekButton)

    def show_deactivable_properties(self):
        self.show_list_widget(self.ui.ListaZastaw, self._curr_player.get_deactivable_properties(), self.ui.ZastawButton)

    def show_activable_properties(self):
        self.show_list_widget(self.ui.ListaWykup, self._curr_player.get_activable_properties(), self.ui.WykupButton)

    def show_player(self, item):
        if item is not None:
            for player in self._game_instance.players:
                if player.get_name() == item.text():
                    self.ui.Pieniadze.setText(str(player.get_cash()))
                    self.ui.ListaPosiadlosci.clear()
                    for property in player.get_properties():
                        self.ui.ListaPosiadlosci.addItem(str(property))
                    break

    def set_properties(self):
        for a in range(0, 40):
            if isinstance(self._board[a], PropertyField):
                property = self._board[a].get_property()
                string = ""
                if not property.is_active():
                    string = "Zastawione"
                if isinstance(property, TypicalProperty):
                    if property.get_apartments_nr() < 5:
                        string = f"Liczba domków : {property.get_apartments_nr()}"
                    else:
                        string = "Hotel"
                if a <= 9:
                    self.ui.gridLayout_2.itemAtPosition(0, a).itemAt(2).widget().setText(string)
                elif a <= 19:
                    self.ui.gridLayout_2.itemAtPosition(a - 10, 10).itemAt(2).widget().setText(string)
                elif a <= 29:
                    self.ui.gridLayout_2.itemAtPosition(10, abs(a - 30)).itemAt(2).widget().setText(string)
                else:
                    self.ui.gridLayout_2.itemAtPosition(abs(a - 40), 0).itemAt(2).widget().setText(string)

    def set_prices(self):
        for a in range(0, 40):
            if isinstance(self._board[a], PropertyField):
                price = str(self._board[a].get_property().get_price())
                if a <= 9:
                    self.ui.gridLayout_2.itemAtPosition(0, a).itemAt(4).widget().setText(price)
                elif a <= 19:
                    self.ui.gridLayout_2.itemAtPosition(a - 10, 10).itemAt(4).widget().setText(price)
                elif a <= 29:
                    self.ui.gridLayout_2.itemAtPosition(10, abs(a - 30)).itemAt(4).widget().setText(price)
                else:
                    self.ui.gridLayout_2.itemAtPosition(abs(a - 40), 0).itemAt(4).widget().setText(price)

    def set_names(self):
        for a in range(0, 40):
            name = self._board[a].get_name()
            if a <= 9:
                self.ui.gridLayout_2.itemAtPosition(0, a).itemAt(0).widget().setText(name)
            elif a <= 19:
                self.ui.gridLayout_2.itemAtPosition(a - 10, 10).itemAt(0).widget().setText(name)
            elif a <= 29:
                self.ui.gridLayout_2.itemAtPosition(10, abs(a - 30)).itemAt(0).widget().setText(name)
            else:
                self.ui.gridLayout_2.itemAtPosition(abs(a - 40), 0).itemAt(0).widget().setText(name)

    def clicked_play(self):
        self.ui.plansze.setCurrentIndex(1)
        self._nr_of_rounds = self.ui.LiczbaRund.value()
        self.end_round = self._nr_of_rounds > 0
        self.turn()
        for player in self._game_instance.players:
            index = 3
            self.ui.gridLayout_2.itemAtPosition(0, 0).itemAt(index).widget().addItem(player.get_name())

    def player_buys(self):
        self._board[self._curr_player.get_position()].buy(self._curr_player)
        self.ui.KupButton.setEnabled(False)
        self.already_buyed = True
        self.update_lists()

    def setupPlayersList(self, name):
        self.ui.ListaGraczy.addItem(name)
        self.ui.ListaGraczyGra.addItem(name)

    def rolled(self):
        result = self._game_instance.roll_dice_result()
        self._game_instance.zero_chance_result()
        self.ui.WynikRzutu.setText(str(result))
        self._already_rolled = True
        self.ui.KupDomekButton.setEnabled(False)
        self.ui.RzutButton.setEnabled(False)
        old_pos = self._curr_player.get_position()
        self._curr_player.move(result)
        new_pos = self._curr_player.get_position()
        if not self._curr_player.is_in_jail():
            self.update_player_pos(old_pos, new_pos)
        self.perform_field_action(new_pos)
        chance_result = self._game_instance.get_chance_result()
        chance_str = ""
        if chance_result > 0:
            chance_str = f"Wygrałeś {chance_result}"
        elif chance_result < 0:
            chance_str = f"Przegrałeś {abs(chance_result)}"
        self.ui.ChanceResult.setText(chance_str)
        self.update_lists()

    def check_buying(self):
        if self._board[self._curr_player.get_position()].can_buy(self._curr_player):
            self.ui.KupButton.setEnabled(True)

    def perform_field_action(self, pos):
        self._game_instance.field_action(pos, self._curr_player)
        if pos == 30:
            self.go_to_jail()
        self.ui.KoniecTuryButton.setEnabled(True)
        self.check_buying()
        self.update_lists()

    def go_to_jail(self):
        self.ui.ListaWiezienie.addItem(self._curr_player.get_name())
        delete_item(self._curr_player.get_name(), self.ui.ListaGoToJail)
        self.ui.WiezienieButton.setEnabled(True)
        self.check_jail()

    def free_of_jail(self):
        delete_item(self._curr_player.get_name(), self.ui.ListaWiezienie)
        self.ui.ListaWiezienieWolni.addItem(self._curr_player.get_name())
        self._game_instance.free_player(self._curr_player)
        if not self._already_rolled:
            self.ui.RzutButton.setEnabled(True)
        self.ui.WiezienieButton.setEnabled(False)
        self.check_jail()
        self.update_lists()

# 0-9 0,pos | 10-19 pos-10,10 | 20-29 10,abs(pos-30) | 30-39  abs(pos-40),0
    def update_player_pos(self, old_pos, new_pos):
        index = 3
        name = self._curr_player.get_name()
        if old_pos <= 9:
            delete_item(name, self.ui.gridLayout_2.itemAtPosition(0, old_pos).itemAt(index).widget())
        elif old_pos <= 19:
            delete_item(name, self.ui.gridLayout_2.itemAtPosition(old_pos - 10, 10).itemAt(index).widget())
        elif old_pos <= 29:
            delete_item(name, self.ui.gridLayout_2.itemAtPosition(10, abs(old_pos - 30)).itemAt(index).widget())
        else:
            delete_item(name, self.ui.gridLayout_2.itemAtPosition(abs(old_pos - 40), 0).itemAt(index).widget())
        if new_pos <= 9:
            self.ui.gridLayout_2.itemAtPosition(0, new_pos).itemAt(index).widget().addItem(name)
        elif new_pos <= 19:
            self.ui.gridLayout_2.itemAtPosition(new_pos - 10, 10).itemAt(index).widget().addItem(name)
        elif new_pos <= 29:
            self.ui.gridLayout_2.itemAtPosition(10, abs(new_pos - 30)).itemAt(index).widget().addItem(name)
        else:
            self.ui.gridLayout_2.itemAtPosition(abs(new_pos - 40), 0).itemAt(index).widget().addItem(name)

    def remove_player_from_board(self, player):
        index = 3
        pos = player.get_position()
        name = player.get_name()
        if pos <= 9:
            delete_item(name, self.ui.gridLayout_2.itemAtPosition(0, pos).itemAt(index).widget())
        elif pos <= 19:
            delete_item(name, self.ui.gridLayout_2.itemAtPosition(pos - 10, 10).itemAt(index).widget())
        elif pos <= 29:
            delete_item(name, self.ui.gridLayout_2.itemAtPosition(10, abs(pos - 30)).itemAt(index).widget())
        else:
            delete_item(name, self.ui.gridLayout_2.itemAtPosition(abs(pos - 40), 0).itemAt(index).widget())

    def add_player(self):
        if self.ui.ListaGraczy.count() < 6 and self.ui.lineEdit.text().strip() != "" and self.ui.lineEdit.text() not in self._used_names:
            self.setupPlayersList(self.ui.lineEdit.text())
            self._used_names.append(self.ui.lineEdit.text())
            self._game_instance.add_player(self.ui.lineEdit.text())
        self.ui.lineEdit.setText("")
        if len(self._used_names) >= 2:
            self.ui.GrajButton.setEnabled(True)
        if len(self._used_names) == 6:
            self.ui.DodajGraczaButton.setEnabled(False)

    def turn(self):
        self._already_rolled = False
        self.already_buyed = False
        self._curr_player = self._game_instance.players[self._curr_player_index]
        if len(self._game_instance.players) == 1:
            self.player_win(self._curr_player.get_name())
        if self.end_round and self._curr_player == self._game_instance.players[0]:
            if self._nr_of_rounds == 0:
                winner_name = self._game_instance.who_wins()
                self.player_win(winner_name)
            self.ui.PozostaloRund.setText(str(self._nr_of_rounds))
        self.ui.Tura.setText(f"Tura gracza : {self._curr_player.get_name()}")
        self.ui.KoniecTuryButton.setEnabled(False)
        self.ui.KupButton.setEnabled(False)
        if not self._curr_player.is_in_jail():
            self.ui.RzutButton.setEnabled(True)
        self.check_jail()
        self.update_properties_selling()
        self.update_lists()

    def end_turn(self):
        self.ui.ChanceResult.setText("")
        if self._curr_player.get_rounds_left() == 1:
            self.free_of_jail()
            self._curr_player.decrement_rounds()
        if self._curr_player.is_in_jail():
            self._curr_player.decrement_rounds()
        self._curr_player_index = (self._curr_player_index + 1) % len(self._game_instance.players)
        if self.end_round and self._curr_player == self._game_instance.players[0]:
            self._nr_of_rounds -= 1
        self.turn()


def gui_main(game, args):
    app = QApplication(args)
    window = MainWindow(game)
    window.showMaximized()
    return app.exec_()


def delete_item(itemName, list):
    items_list = list.findItems(itemName, QtCore.Qt.MatchExactly)
    for item in items_list:
        list.takeItem(list.row(item))
