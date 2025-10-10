import json
import os
from datetime import datetime

class TicketManager:
    def __init__(self):
        self.tickets_file = "active_tickets.json"
        self.load_tickets()
    
    def load_tickets(self):
        """Carica i ticket attivi dal file"""
        try:
            if os.path.exists(self.tickets_file):
                with open(self.tickets_file, 'r', encoding='utf-8') as f:
                    self.active_tickets = json.load(f)
            else:
                self.active_tickets = {}
        except Exception as e:
            print(f"❌ Errore caricamento ticket: {e}")
            self.active_tickets = {}
    
    def save_tickets(self):
        """Salva i ticket attivi nel file"""
        try:
            with open(self.tickets_file, 'w', encoding='utf-8') as f:
                json.dump(self.active_tickets, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Errore salvataggio ticket: {e}")
    
    def add_ticket(self, channel_id, ticket_data):
        """Aggiunge un ticket attivo"""
        self.active_tickets[str(channel_id)] = {
            **ticket_data,
            "created_at": datetime.now().isoformat()
        }
        self.save_tickets()
    
    def remove_ticket(self, channel_id):
        """Rimuove un ticket"""
        channel_id = str(channel_id)
        if channel_id in self.active_tickets:
            del self.active_tickets[channel_id]
            self.save_tickets()
    
    def get_all_tickets(self):
        """Restituisce tutti i ticket attivi"""
        return self.active_tickets

# Istanza globale del ticket manager
ticket_manager = TicketManager()
