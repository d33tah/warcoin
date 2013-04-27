import random

class Jednostka:
    
    def __init__(self, plansza, x, y, czyja):
        self.czyja = czyja
        self.ile_hp = 1
        self.plansza = plansza
        self.x, self.y = x, y
        self.klucz_szyfrujacy = ''.join([ chr(random.randint(0, 255)) for _ in range(16)])
        self.wykonano_ruch = False
    
    @classmethod
    def dopisz(cls, plansza, x, y, czyja):
        plansza[x][y] = Jednostka(plansza,x,y, czyja)
        
    def dodaj_punkt(self):
        self.ile_hp += 1
        
    def przesun(self, x, y):
        self.plansza[self.x][self.y] = None
        self.plansza[x][y] = self
    
    def zabierz_punkt(self):
        self.ile_hp -= 1
        
    def __str__(self):
        """Do przycisku"""
        if not self.czyja:
            return "?"
        else:
            return str(self.ile_hp)
        