import customtkinter as ctk
from datetime import datetime, timedelta
import threading
import time

# Set the default appearance and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class AuctionItem:
    def __init__(self, name, starting_price, duration_minutes, description=None):
        self.name = name
        self.current_price = starting_price
        self.starting_price = starting_price
        self.highest_bidder = "No bids yet"
        self.end_time = datetime.now() + timedelta(minutes=duration_minutes)
        self.active = True
        self.bid_history = []
        self.description = description
        self.min_increment = starting_price * 0.05  # 5% minimum increment

class AuctionApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Modern Auction System")
        self.root.geometry("1200x800")
        
        # Sample auction items
        self.items = [
            AuctionItem(
                "Vintage Rolex Submariner",
                1000,
                60,
                "A stunning 1960s Rolex Submariner ref. 5513. Original dial, pristine condition. Includes box and papers."
            ),
            AuctionItem(
                "Ming Dynasty Vase",
                2500,
                45,
                "Exquisite 15th century Ming vase featuring traditional blue and white porcelain. Height: 30cm. Museum quality."
            ),
            AuctionItem(
                "Monet Original Sketch",
                5000,
                30,
                "Rare preliminary sketch by Claude Monet. Dated 1923. Authenticated by Christie's. Size: 20x30cm."
            )
        ]
        
        self.setup_gui()
        self.update_thread = threading.Thread(target=self.update_times, daemon=True)
        self.update_thread.start()
    
    def setup_gui(self):
        # Create main layout with enhanced padding
        self.sidebar = ctk.CTkFrame(self.root, width=350)
        self.sidebar.pack(side="left", fill="y", padx=20, pady=20)
        self.sidebar.pack_propagate(False)
        
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        self.create_sidebar()
        self.create_main_content()
    
    def create_sidebar(self):
        # Title
        ctk.CTkLabel(
            self.sidebar,
            text="Bid Control Panel",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=20)
        
        # Quick bid section
        quick_bid_frame = ctk.CTkFrame(self.sidebar)
        quick_bid_frame.pack(pady=15, fill="x", padx=20)
        
        ctk.CTkLabel(
            quick_bid_frame,
            text="Quick Bid",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=5)
        
        btn_frame = ctk.CTkFrame(quick_bid_frame)
        btn_frame.pack(fill="x")
        
        for amount in ["50", "100", "500"]:
            ctk.CTkButton(
                btn_frame,
                text=f"+${amount}",
                command=lambda a=amount: self.quick_bid(float(a)),
                height=35
            ).pack(side="left", padx=5, pady=5, expand=True)
        
        # Item selection
        ctk.CTkLabel(
            self.sidebar,
            text="Select Item",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 5))
        
        self.selected_item = ctk.CTkComboBox(
            self.sidebar,
            values=[item.name for item in self.items],
            width=300,
            command=self.on_item_selected
        )
        self.selected_item.pack(pady=10)
        
        # Item details
        self.item_details = ctk.CTkTextbox(self.sidebar, height=200, width=300)
        self.item_details.pack(pady=10)
        
        # Bidding controls
        ctk.CTkLabel(
            self.sidebar,
            text="Your Information",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 5))
        
        self.bidder_name = ctk.CTkEntry(
            self.sidebar,
            width=300,
            placeholder_text="Enter your name"
        )
        self.bidder_name.pack(pady=10)
        
        self.bid_amount = ctk.CTkEntry(
            self.sidebar,
            width=300,
            placeholder_text="Enter bid amount ($)"
        )
        self.bid_amount.pack(pady=10)
        
        # Bid button
        self.bid_button = ctk.CTkButton(
            self.sidebar,
            text="Place Bid",
            command=self.place_bid,
            width=300,
            height=40,
            corner_radius=32,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.bid_button.pack(pady=20)
        
        # Theme switcher
        ctk.CTkLabel(
            self.sidebar,
            text="Appearance",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 5))
        
        self.appearance_mode = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Dark", "Light", "System"],
            command=self.change_appearance_mode,
            width=300
        )
        self.appearance_mode.pack(pady=10)
    
    def create_main_content(self):
        ctk.CTkLabel(
            self.main_frame,
            text="Live Auctions",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack(pady=20)
        
        self.items_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.items_frame.pack(fill="both", expand=True)
        
        self.item_cards = []
        self.update_items_display()
    
    def create_item_card(self, item):
        card = ctk.CTkFrame(self.items_frame)
        card.pack(fill="x", padx=10, pady=10)
        
        # Item name
        ctk.CTkLabel(
            card,
            text=item.name,
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=10)
        
        # Price and bidder info
        price_label = ctk.CTkLabel(
            card,
            text=f"Current Bid: ${item.current_price:,.2f}",
            font=ctk.CTkFont(size=18)
        )
        price_label.pack(pady=5)
        
        bidder_label = ctk.CTkLabel(
            card,
            text=f"Highest Bidder: {item.highest_bidder}",
            font=ctk.CTkFont(size=16)
        )
        bidder_label.pack(pady=5)
        
        # Time remaining
        time_label = ctk.CTkLabel(
            card,
            text="Time Remaining: Calculating...",
            font=ctk.CTkFont(size=16)
        )
        time_label.pack(pady=5)
        
        progress = ctk.CTkProgressBar(card, width=400)
        progress.pack(pady=10)
        progress.set(1)
        
        # Bid history button
        ctk.CTkButton(
            card,
            text="View Bid History",
            command=lambda: self.show_bid_history(item),
            width=150
        ).pack(pady=10)
        
        return {
            "frame": card,
            "price_label": price_label,
            "bidder_label": bidder_label,
            "time_label": time_label,
            "progress": progress
        }
    
    def quick_bid(self, amount):
        if not self.selected_item.get():
            self.show_error("Please select an item first")
            return
            
        current_item = next((item for item in self.items if item.name == self.selected_item.get()), None)
        if current_item:
            self.bid_amount.delete(0, 'end')
            self.bid_amount.insert(0, str(current_item.current_price + amount))
    
    def on_item_selected(self, choice):
        selected_item = next((item for item in self.items if item.name == choice), None)
        if selected_item:
            self.item_details.delete('1.0', 'end')
            self.item_details.insert('1.0', f"Description: {selected_item.description}\n\n")
            self.item_details.insert('end', f"Starting Price: ${selected_item.starting_price:,.2f}\n")
            self.item_details.insert('end', f"Current Price: ${selected_item.current_price:,.2f}\n")
            self.item_details.insert('end', f"Min Increment: ${selected_item.min_increment:,.2f}\n")
    
    def update_items_display(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        self.item_cards = []
        
        for item in self.items:
            if item.active:
                card = self.create_item_card(item)
                self.item_cards.append((item, card))
    
    def update_times(self):
        while True:
            for item, card in self.item_cards:
                if item.active:
                    time_left = item.end_time - datetime.now()
                    total_duration = timedelta(minutes=60)
                    progress = max(0, min(1, time_left.total_seconds() / total_duration.total_seconds()))
                    
                    if time_left.total_seconds() > 0:
                        time_str = str(timedelta(seconds=int(time_left.total_seconds())))
                        card["time_label"].configure(text=f"Time Remaining: {time_str}")
                        card["progress"].set(progress)
                    else:
                        card["time_label"].configure(text="Auction Ended")
                        card["progress"].set(0)
                        item.active = False
                    
                    card["price_label"].configure(text=f"Current Bid: ${item.current_price:,.2f}")
                    card["bidder_label"].configure(text=f"Highest Bidder: {item.highest_bidder}")
            
            time.sleep(1)
    
    def place_bid(self):
        if not self.selected_item.get() or not self.bidder_name.get() or not self.bid_amount.get():
            self.show_error("Please fill in all fields")
            return
        
        try:
            bid_amount = float(self.bid_amount.get())
        except ValueError:
            self.show_error("Bid amount must be a number")
            return
        
        selected_item = next((item for item in self.items if item.name == self.selected_item.get()), None)
        
        if not selected_item:
            self.show_error("Please select a valid item")
            return
        
        if not selected_item.active:
            self.show_error("This auction has ended")
            return
        
        if bid_amount <= selected_item.current_price:
            self.show_error(f"Bid must be higher than current price (${selected_item.current_price:,.2f})")
            return
        
        selected_item.bid_history.append({
            'bidder': self.bidder_name.get(),
            'amount': bid_amount,
            'time': datetime.now()
        })
        
        selected_item.current_price = bid_amount
        selected_item.highest_bidder = self.bidder_name.get()
        self.show_success("Bid placed successfully!")
    
    def show_bid_history(self, item):
        dialog = ctk.CTkToplevel()
        dialog.title(f"Bid History - {item.name}")
        dialog.geometry("400x500")
        
        ctk.CTkLabel(
            dialog,
            text="Bid History",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        history_frame = ctk.CTkScrollableFrame(dialog)
        history_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        if item.bid_history:
            for bid in reversed(item.bid_history):
                bid_frame = ctk.CTkFrame(history_frame)
                bid_frame.pack(fill="x", pady=5)
                
                ctk.CTkLabel(
                    bid_frame,
                    text=f"{bid['bidder']}",
                    font=ctk.CTkFont(weight="bold")
                ).pack(pady=5)
                
                ctk.CTkLabel(
                    bid_frame,
                    text=f"${bid['amount']:,.2f}"
                ).pack()
                
                ctk.CTkLabel(
                    bid_frame,
                    text=bid['time'].strftime("%Y-%m-%d %H:%M:%S"),
                    font=ctk.CTkFont(size=12)
                ).pack(pady=5)
        else:
            ctk.CTkLabel(
                history_frame,
                text="No bids yet"
            ).pack(pady=20)
        
        ctk.CTkButton(
            dialog,
            text="Close",
            command=dialog.destroy,
            width=200
        ).pack(pady=20)
    
    def show_error(self, message):
        dialog = ctk.CTkToplevel()
        dialog.title("Error")
        dialog.geometry("400x200")
        
        ctk.CTkLabel(dialog, text=message).pack(pady=20)
        ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=10)
    
    def show_success(self, message):
        dialog = ctk.CTkToplevel()
        dialog.title("Success")
        dialog.geometry("400x200")
        
        ctk.CTkLabel(dialog, text=message).pack(pady=20)
        ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=10)
    
    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode.lower())
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AuctionApp()
    app.run()
