from typing import Any, Text, Dict, List
import re

import pymongo as pymongo
from pymongo import MongoClient

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType
from rasa_sdk.events import AllSlotsReset
from rasa_sdk.types import DomainDict
from datetime import date, datetime

VALORI_CONSENTITI_CIRCUITO = ["visa", "mastercard", "diners", "american express", "china union pay", "jcb"]
NOTEBOOK_DISPONIBILI = ["macbook pro 16 m1", "acer-a114-33-c28d"]
pattern_visa = "^4[0-9]{12}(?:[0-9]{3})?$"
pattern_visa_mastercard = "^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})$"
pattern_diners = "^3(?:0[0-5]|[68][0-9])[0-9]{11}$"
pattern_mastercard = "^(5[1-5][0-9]{14}|2(22[1-9][0-9]{12}|2[3-9][0-9]{13}|[3-6][0-9]{14}|7[0-1][0-9]{13}|720[0-9]{12}))$"
pattern_jcb = "^(?:2131|1800|35\d{3})\d{11}$"
pattern_union = "^(62[0-9]{14,17})$"
pattern_intestatario = "^([a-z]+[,.]?[ ]?|[a-z]+['-]?)+$"
pattern_cvv = "^\d{3}$"
pattern_scadenza = "^(0[1-9]|1[0-2])\/?([0-9]{2})$"
pattern_email = "^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$"
pattern_numero_telefono = "^((00|\+)39[\. ]??)??3\d{2}[\. ]??\d{6,7}$"
pattern_indirizzo_spedizione = "^\s*\S+(?:\s+\S+){2}"
pattern_cap = "^\d{5}$"

class ValidazioneFormOrdine(FormValidationAction):

    def name(self) -> Text:
        return "validate_form_ordine"

    def validate_circuito(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate 'circuito'."""

        if slot_value.lower() not in VALORI_CONSENTITI_CIRCUITO:
            dispatcher.utter_message(text=f"Si accettano solo i seguenti circuiti: VISA, MASTERCARD, DINERS, AMERICAN EXPRESS, JCB e CHINA UNION PAY")
            return {"circuito":None}
        dispatcher.utter_message(text=f"OK! Il circuito della tua carta di credito è stato accettato!")
        return {"circuito": slot_value}

        
    
    def validate_numero_carta(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate 'numero_carta'."""
        string_card = str(slot_value).replace(" ","").replace("-","")
        if re.match(pattern_visa,str(string_card)) or re.match(pattern_visa_mastercard,str(string_card)) is not None:
            dispatcher.utter_message(text=f"Il numero della carta VISA o VISA MASTERCARD è corretto!")
            return {"numero_carta": slot_value}          
        elif re.match(pattern_diners, str(string_card)) is not None:
            dispatcher.utter_message(text=f"Il numero della carta DINERS è corretto!")
            return {"numero_carta": slot_value}
        elif re.match(pattern_mastercard, str(string_card)) is not None:
            dispatcher.utter_message(text=f"Il numero della carta MASTERCARD è corretto!")
            return {"numero_carta": slot_value}
        elif re.match(pattern_jcb, str(string_card)) is not None:
            dispatcher.utter_message(text=f"Il numero della carta JCB è corretto!")
            return {"numero_carta": slot_value}
        elif re.match(pattern_union, str(string_card)) is not None:
            dispatcher.utter_message(text=f"Il numero della carta UNION è corretto!")
            return {"numero_carta": slot_value}
        else:           
            dispatcher.utter_message(text=f"Il numero di carta è errato, riprova")
            return {"numero_carta":None}            
        
    def validate_intestatario_carta(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate 'intestatario_carta'."""

        if re.match(pattern_intestatario,str(slot_value)) is not None:
            dispatcher.utter_message(text=f"Inserisci un intestatario valido!")
            return {"intestatario_carta":None}
        dispatcher.utter_message(text=f"OK!")
        return {"intestatario_carta": slot_value}

    def validate_cvv(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate 'cvv'."""

        if re.match(pattern_cvv, str(slot_value)) is not None:
            dispatcher.utter_message(text=f"Il cvv inserito è corretto!")
            return {"cvv": slot_value}
        else:
            dispatcher.utter_message(text=f"Il cvv inserito è errato, riprova")
            return {"cvv": None}

    def validate_scadenza(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate 'scadenza'."""

        past = datetime.strptime(slot_value, "%m/%y")
        present_string = datetime.today().strftime('%m/%y')
        present_datetime = datetime.strptime(present_string, '%m/%y')
        
        if (re.match(pattern_scadenza, str(slot_value)) is not None and (past.date() > present_datetime.date())):
            dispatcher.utter_message(text=f"La data di scadenza è corretta!")
            return {"scadenza": slot_value}
        else:
            dispatcher.utter_message(text=f"La data di scadenza è errata, riprova")
            return {"scadenza": None}
    
    def validate_nome_prodotto(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate 'nome_prodotto'."""

        print(slot_value.lower())
        if slot_value.lower() not in NOTEBOOK_DISPONIBILI:
            dispatcher.utter_message(text=f"Al momento il prodotto non è disponibile")
            return {"nome_prodotto":None}
        dispatcher.utter_message(text=f"Il prodotto è disponibile!")
        return {"nome_prodotto": slot_value}
    
    def validate_quantita(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate 'quantita'."""

        slot_value_num = int(slot_value)
        if slot_value_num > 0 and slot_value_num < 11:
            dispatcher.utter_message(text=f"OK!")
            return {"quantita": slot_value}
        dispatcher.utter_message(text=f"Quantità non valida")
        return {"quantita": None}

    def validate_email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate 'email'."""

        if (re.match(pattern_email, str(slot_value)) is not None):
            dispatcher.utter_message(text=f"OK!")
            return {"email": slot_value}
        else:
            dispatcher.utter_message(text=f"L'email non è corretta!")
            return {"email": None}
    
    def validate_numero_telefono(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate 'numero_telefono'."""

        if re.match(pattern_numero_telefono, str(slot_value)) is not None:
            dispatcher.utter_message(text=f"OK! Il numero inserito è stato accettato!")
            return {"numero_telefono": slot_value}
        else:
            dispatcher.utter_message(text=f"Il numero di telefono inserito non è valido, riprova")
            return {"numero_telefono": None}
    
    def validate_indirizzo_spedizione(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate 'indirizzo_spedizione'."""

        if re.match(pattern_indirizzo_spedizione, str(slot_value)) is not None:
            dispatcher.utter_message(text=f"L'indirizzo di spedizione è corretto!")
            return {"indirizzo_spedizione": slot_value}
        else:
            dispatcher.utter_message(text=f"L'indirizzo non è valido, riprova")
            return {"indirizzo_spedizione": None}
    
    def validate_cap(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate 'cap'."""

        if re.match(pattern_cap, str(slot_value)) is not None:
            dispatcher.utter_message(text=f"Il CAP è corretto!")
            return {"cap": slot_value}
        else:
            dispatcher.utter_message(text=f"Il CAP non è valido, riprova")
            return {"cap": None}
 


    def validate_conferma_recap(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate 'conferma_recap'."""

        if tracker.get_slot("conferma_recap") == "si_recap":
            circuito = tracker.get_slot("circuito")
            numero_carta = tracker.get_slot("numero_carta")
            intestatario_carta = tracker.get_slot("intestatario_carta")
            scadenza = tracker.get_slot("scadenza")
            cvv = tracker.get_slot("cvv")
            nome_prodotto = tracker.get_slot("nome_prodotto")
            quantita = tracker.get_slot("quantita")
            email = tracker.get_slot("email")
            numero_telefono = tracker.get_slot("numero_telefono")
            indirizzo_spedizione = tracker.get_slot("indirizzo_spedizione")
            citta = tracker.get_slot("citta")
            cap = tracker.get_slot("cap")

            dispatcher.utter_message(text="Riepilogo ordine:\n"+
                                      "Circuito carta di credito: "+str(circuito)+"\n"+
                                      "Numero carta di credito: "+str(numero_carta)+"\n"+
                                      "Intestatario carta: "+str(intestatario_carta)+"\n"+
                                      "Scadenza carta: "+str(scadenza)+"\n"+
                                      "CVV carta: "+str(cvv)+"\n"
                                      "Nome prodotto: "+str(nome_prodotto)+"\n"+
                                      "Quantità: "+str(quantita)+"\n"+
                                      "E-mail: "+str(email)+"\n"+
                                      "Numero di telefono: "+str(numero_telefono)+"\n"+
                                      "Indirizzo spedizione: "+str(indirizzo_spedizione)+" "+str(citta)+"\n"+
                                      "CAP: "+str(cap))
            return {"conferma_recap": slot_value}
        if tracker.get_slot("conferma_recap") == "no_recap":
            return {"conferma_recap": slot_value}

    def validate_conferma_ordine(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate 'conferma_ordine'."""

        if tracker.get_slot("conferma_ordine") == "si_ordine":
            client = MongoClient('mongodb+srv://admin:admin@cluster0.rh2yb.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
            db = client.test_database
            collection = db.test_collection
            ordini = db.ordini

            circuito = tracker.get_slot("circuito")
            numero_carta = tracker.get_slot("numero_carta")
            intestatario_carta = tracker.get_slot("intestatario_carta")
            scadenza = tracker.get_slot("scadenza")
            cvv = tracker.get_slot("cvv")
            nome_prodotto = tracker.get_slot("nome_prodotto")
            quantita = tracker.get_slot("quantita")
            email = tracker.get_slot("email")
            numero_telefono = tracker.get_slot("numero_telefono")
            indirizzo_spedizione = tracker.get_slot("indirizzo_spedizione")
            citta = tracker.get_slot("citta")
            cap = tracker.get_slot("cap")
                
            ricevuta = {
                    "numero_carta": numero_carta,
                    "intestatario_carta": intestatario_carta,
                    "scadenza": scadenza,
                    "cvv": cvv,
                    "nome_prodotto": nome_prodotto,
                    "quantita": quantita,
                    "email": email,
                    "numero_telefono": numero_telefono,
                    "indirizzo_spedizione": indirizzo_spedizione,
                    "citta": citta,
                    "cap": cap,
                    "emissione_ricevuta" : datetime.today().strftime('%d/%m/%y')
            }

            #salva la ricevuta a db e ritorna l'id del documento appena creato
            ordini.insert_one(ricevuta)
  
            dispatcher.utter_message(text=f"L'ordine è stato inoltrato")
            return {"conferma_ordine": slot_value}
        else:
            dispatcher.utter_message(text=f"L'ordine è stato annullato")
            return {"conferma_ordine": slot_value}
 

class ActionReset(Action):

    def name(self) -> Text:
        return "action_reset"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return[AllSlotsReset()]