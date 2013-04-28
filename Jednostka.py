import random
import config as c

class Jednostka:
    
    def __init__(self, protokol, x, y, czyja):
        self.czyja = czyja
        self.ile_hp = 1
        self.protokol = protokol
        self.plansza = protokol.plansza
        self.x, self.y = x, y
        self.klucz_szyfrujacy = ''.join([ chr(random.randint(0, 255)) for _ in range(16)])
        self.wykonano_ruch = False
    
    @classmethod
    def dopisz(cls, protokol, x, y, czyja):
        utworzona = Jednostka(protokol,x,y, czyja)
        protokol.plansza[x][y] = utworzona
        protokol.jednostki += [utworzona]
        
    def dodaj_punkt(self):
        self.ile_hp += 1
        
    def przesun(self, x, y):
        self.plansza[self.x][self.y] = None
        self.plansza[x][y] = self
        self.x, self.y = x, y
    
    def zabierz_punkt(self):
        self.ile_hp -= 1
        
    def __str__(self):
        """Do przycisku"""
        if not self.czyja:
            return "?"
        else:
            return str(self.ile_hp)
        
    def obok_przeciwnik(self):
        x, y = self.x, self.y
        mozliwe_pozycje = [ (xx, yy) 
                           for xx in [x-1, x, x+1] 
                           for yy in [y-1, y, y+1] 
                           if not (xx==x and yy==y) 
                           and xx>=0 and xx<c.wielkosc_planszy
                           and yy>=0 and yy<c.wielkosc_planszy ]
        for xx, yy in mozliwe_pozycje:
            jednostka = self.plansza[xx][yy]
            if jednostka is not None and not jednostka.czyja:
                return True
        return False
        