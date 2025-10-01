# 2D: Fourierova Transformace (3D)

Plugin zobrazující 3D Fourierovu transformaci v Kritě. Vstupem je několik layerů s obrázky velikosti max 128x128 px. Výstupem je pak sada složek, ve kterých se nachází FT jednotlivých vrstev - power, phase a magnitude spectrum, a také zkombinovaný FT výstup pomocí phase a magnitude spektra.

### Update
V pluginu byla po odevzdání nalezena chyba - třetí dimenze nebyla správně přičítána ke zbytku součtu, a plugin byl kvůli tomu degradován na sadu 2D FT. Tato chyba byla opravena, a přibyl kvůli tomu požadavek na stejné dimenze u všech vrstev obrázku. Následně byl také napraven fakt, že při erroru u obrázku s většími dimenzemi než povolenými byly zobrazené 2 errory za sebou (poznatek z komentáře v Grades). Změny v dokumentaci po update budou napsané kurzívou.

![bitmap - obrázek](2d.png "EDIT|UPLOAD")

![bitmap - video](2d.mp4 "EDIT|UPLOAD")

#### Instalace
Plugin je potřeba vložit do složky Krity pro pluginy, tedy na cestě "Krita (x64)/share/krita/pykrita". Po zapnutí Krity je nutné plugin zpřístupnit v Settings -> Configure Krita... -> Python Plugin Manager -> zatrhnout FT3D.

## Uživatelská dokumentace
Vstupem je 1 až x vrstev obrázků *stejných rozměrů* velikosti maximálně 128x128 px. Plugin lze spustit kliknutím na Tools -> Scripts -> Fourier Transform 3D. Poté už je potřeba jen počkat než program vypočítá FT, a objeví se x složek s výstupy.

## Teoretická dokumentace

### RGB to Grayscale
Převedení obrázku z RGB do odstínů šedi (grayscale) je prvním krokem při zpracování obrazu pro FT. Pro převedení klasického RGB obrázku na grayscale je potřeba nějakým způsobem sečíst vyváženou průměrnou hodnotu R, G a B hodnot. Ale jak přesně ji vyvážit? Lidé například vnímají zelenou asi 10x světlejší, než modrou. Psychologové pomocí experimentů zjistili přesné hodnoty, jak vyvážit tyto 3 kanály tak, aby stále odpovídaly tomu, jak jasy vnímá člověk.<br/>
![Výpočet jasu podle psychologů](./RGBtoGrayPsychologistsFormula.png)<br/>
Každopádně, očima vnímáme změny v nízkých jasech o dost dramatičtěji, než ve vysokých jasech. Proto je zbytečné se tolik zaměřovat na malé změny ve vysokých hodnotách jasu, a více se zaměřit na detailnější reprezentaci nízkých hodnot jasu. O to se typicky stará gamma komprese, ale pracuje se s ní složitě, a při určitých operacích je potřeba dekompresovat a pak zpátky kompresovat. Proto je nejlepší volbou lineární aproximace, která dává podobné výsledky jako gamma komprese a nemá žádné problémy se složitostí.<br/>
![Lineární aproximace gamma komprese](./RGBtoGrayLinearApproximation.png)<br/>

Zdroj: https://e2eml.school/convert_rgb_to_grayscale#:~:text=An%20intuitive%20way%20to%20convert,into%20a%20reasonable%20gray%20approximation.

### Fourierova transformace - 1D
V 1D Fourierově transformaci se zabýváme kmitáním signálu - zvuky. Jde o to, že jakýkoli zvukový signál lze popsat jako součet jednoduchých bázových sinusových a kosinusových signálů. Nehledě na to, jak složitě výsledný zvuk vypadá, je složen z x bázových signálů. 1D transformace vrací dvě hlavní složky:
- Magnituda (velikost) - Jak silně je daná frekvence zastoupena v signálu
- Fáze - Její posun

### Fourierova transformace - 2D
2D Fourierova transformace je rozšířená 1D FT do dvou rozměrů. Používá se pro zpracování obrázků, je velmi užitečná co se týče například pravidelných závad, nebo šumu. Ve FT reprezentaci obrázku tyto nedokonalosti můžeme vidět velmi dobře, dají se zde velmi snadno napravit a poté pomocí inverzní FT převést zpět na původní opravený obrázek.
Vrací 3 hlavní složky:
- Magnituda - Intenzita jednotlivých frekvencí
- Phase - Posun frekvencí
- Power - Magnituda na druhou - větší intenzita

### Fourierova transformace - 3D
3D Fourierova transformace je rozšířená 2D Fourierova transformace na trojrozměrná data, například objemové modely (3D textury nebo sady obrázků). Každý objemový datový bod má svou hodnotu intenzity, která je analyzovaná ve třech dimenzích. Vrací stejné složky jako 2D FT.

### Diskrétní fourierova transformace
Matematický vzorec, pomocí kterého jsme schopni rozložit zvuky nebo obrázky na jejich bázové části. Z tohoto vzorce dokážeme získat výše zmíněné složky - magnitudu, fázi a power. <br/>![DFT](./DFTvzorec.png) <br/>
Tento vzorec je poměrně složitý na výpočet, takže existuje algoritmus Fast Fourier Transform, který je založen na základě stejného vzorce, ale pracuje efektivněji. Tento algoritmus je již implementován v knihovně numpy, každopádně tento plugin je psán ručně pomocí diskrétní fourierovy transformace. Pro rozšíření FT do 2D a 3D je pak potřeba akorát přidat další proměnnou. <br/>![2D DFT](./2DDFTvzorec.png)<br/> ![3D DFT](./3DDFTvzorec.png)<br/> Pro lepší viditelnost je dobré logaritmicky vyškálovat výsledek pomocí log(1+val).

### Shift 2D
Shiftování (posun) 2D DFT je technika, která přesouvá nulovou frekvenci do středu obrázku. Tímto způsobem je frekvenční spektrum lépe viditelné. Přesunutí se provádí výměnou čtvrtin obrázku:

Levý horní roh se vymění s pravým dolním rohem.
Pravý horní roh se vymění s levým dolním rohem.
Tento posun zajišťuje, že nízkofrekvenční složky jsou umístěny uprostřed obrazu a vysokofrekvenční složky na okrajích.

### Kombinace magnitudy a phase spektra
Pro lepší znázornění FT můžeme kombinovat magnitude a phase spektrum. Magnitudu můžeme například použít jako hodnotu jasu, a fázi pro barevný odstín. Pak by saturace byla buď 1, nebo by mohla také záviset na magnitudě.<br/> V tomto pluginu ale zůstáváme u grayscale znázornění. Používáme vzorec ``Brightness = NormalizedMagnitude × ( 1 + 0.5 × PhaseNormalized )``. Normalizovanou magnitudu na "[0, 1]" získáme takto:<br/>

1) Zjistíme maximální hodnotu magnitudy: ``max_magnitude = max(max(row) for row in magnitude)``<br/>
2) Normalizujeme dělením nejvyšší možnou magnitudou: ``normalized_magnitude = [[val / max_magnitude for val in row] for row in magnitude] ``<br/>
3) Normalizujeme fázi: ``phase_normalized = (phase[y][x] + math.pi) / (2 * math.pi)``<br/>
4) Vypočítáme jas pomocí vzorce: ``brightness = normalized_magnitude[y][x] * (1 + 0.5 * phase_normalized) ``<br/>
5) Znormalizujeme samotný jas:`` brightness = max(0, min(brightness, 1))``<br/>
6) Naškálujeme ho na 255, a také naschvál trochu jas snížíme, protože by byl jinak moc světlý: ``grayscale_image[y][x] = int(brightness * 255 * 0.5)``<br/>

### Normalizace
Pro zobrazení výsledků je potřeba provést normalizaci - škálování dat na rozmezí [0,255]. Postup:<br/>
1) Najdeme globální minimum a maximum. Pokud jsou tyto hodnoty stejné, znamená to, že všechny pixely mají stejný jas, a tedy normalizace není možná - vrátíme nuly.<br/>
2) Vypočítáme škálu pomocí vzorce: ``scale = 255 / (max - min)``<br/>
3) Provedeme normalizaci a gamma korekci (zadanou jako argument funkce) pomocí vzorce ``(val - min) * scale * gamma``.

## Programátorská dokumentace

### Struktura
Vše je umístěno v jedné třídě, která dědí z Extension a nazývá se FourierTransformPlugin.

### Proměnné třídy
- x_coords: Uchovává x souřadnice pro horní levé rohy obrázků.
- y-coords: Uchovává y souřadnice pro horní levé rohy obrázků.

### Metody
#### `__init(self, parent)__`
Inicializuje instanci pluginu.
#### `__setup(self)__`
Volá se při inicializaci pluginu do Krity.
#### `__createActions(self, window)__`
Vytváří akci pro menu pluginu do menu "tools/scripts" a naváže ji na metodu apply_fourier_transform.<br/>
__Parametr__:<br/>
window - okno Krity
#### `__apply_fourier_transform(self)__`
Vypočítá a zobrazí 3D Fourierovu transformaci. Kontroluje podmínky jako aktivní dokument, existující vrstvu apod.<br/>
__Kroky:__<br/>
a) Zkontroluje, zda existuje aktivní dokument.<br/>
b) Získá seznam vrstev dokumentu.<br/>
c) Převede vrstvy na grayscale pomocí metody nodes_to_grayscale.<br/>
d) Provede 3D DFT pomocí compute_dft_3d.<br/>
e) Normalizuje výsledná data pomocí normalize.<br/>
f) Vykreslí výsledky (combined, magnitude, phase a power spectrum) pomocí show_result_3d.<br/>
#### `__nodes_to_grayscale(self, nodes)__`
Převádí pole RGB nodes na grayscale. Vrací pole grayscale nodes. Pokud je jakákoli z vrstev větší než 128x128 pixelů, plugin vyhodí error.
#### `__compute_dft_3D(self, volume)__`
Vypočítá 3D Diskrétní Fourierovu transformaci na zadaném poli obrázků. Pro lepší viditelnost logaritmicky škáluje magnitude a power spektrum. Volá také funkci shift_dft_2d na jednotlivé obrázky pro posunutí nulové frekvence doprostřed.<br/>
__Návratová hodnota:__<br/>
combined - Kombinované fázové a power spektrum<br/>
magnitude - Magnitude spektrum<br/>
phase - Fázové spektrum<br/>
power - Výkonové spektrum<br/>
#### `__shift_dft_2d(self, data)__`
Přesune nulovou frekvenci doprostřed obrázku.<br/>
__Parametry:__ data - obrázek<br/>
__Návratová hodnota:__ shifted - posunutý obrázek
#### `__combine_magnitude_phase(self, magnitude, phase)__`
Kombinuje magnitudu a fázi do jednoho spektra.<br/>
__Parametry__:<br/>
magnitude - data phase spektra<br/>
phase - data fázového spektra<br/>
__Návratová hodnota:__<br/>
2D grayscale obrázek.
#### `__normalize(self, data, gamma)__`
Normalizuje sadu dat na rozsah [0, 255] a aplikuje gamma korekci.<br/>
__Parametry:__<br/>
data - obrázek<br/>
gamma - škálovací hodnota<br/>
__Návratová hodnota:__<br/>
Normalizovaná sada dat, nebo pole nul, když mají všechna data stejnou hodnotu.
#### `__show_result_3d(self, result, title)__`
Zobrazí výsledné 3D spektrum po vrstvách pomocí volání show_result_2d.
__Parametry:__<br/>
result - sada výsledných dat<br/>
title - název vrstvy<br/>
#### `__show_result(self, result, title, index)__`
Vytvoří novou vrstvu, vyhledá složku do které vrstva patří pomocí metody find_group_by_name. Následně vyplní vrstvu výslednými daty (result) a vloží ji do nalezené složky.<br/>
__Parametry:__<br/>
result - výsledná data<br/>
title - název vrstvy<br/>
index - index vrstvy<br/>
#### `__find_group_by_name(self, parent_node, group_name)__`
Zkusí vyhledat složku se specifikovaným názvem a vrátí ji. Pokud ji nenajde, vytvoří ji.<br/>
__Parametry:__<br/>
parent_node - rodičovská složka ve které se má daná složka hledat<br/>
group_name - název složky, která se hledá<br/>
__Návratová hodnota:__<br/>
Odkaz na složku pokud je nalezena, jinak None.
<br/><br/><br/>
### Vývoj
Před začátkem tvorby pluginu jsem pro pochopení FT zhlédla následující videa na Youtube:<br/>
- Restoring a picture using the FOURIER TRANSFORM!: https://www.youtube.com/watch?v=bpn3DEULv8g&pp=ygUZZm91cmllciB0cmFuc2Zvcm0gMmQgZ2ltcA%3D%3D <br/>
- 2D Fourier Transform - An Example: https://www.youtube.com/watch?v=js4bLBYtJwY&t=65s&pp=ygUZZm91cmllciB0cmFuc2Zvcm0gMmQgZ2ltcA%3D%3D  <br/>
- But what is the Fourier Transform? A visual introduction.: https://www.youtube.com/watch?v=spUNpyF58BY&t=477s&pp=ygUZZm91cmllciB0cmFuc2Zvcm0gMmQgZ2ltcA%3D%3D <br/>
- Image Processing with Fourier Transform: https://www.youtube.com/watch?v=oACegp4iGi0&t=47s&pp=ygUZZm91cmllciB0cmFuc2Zvcm0gMmQgZ2ltcA%3D%3D <br/><br/>
- Pro vývoj pluginu jsem si prošla kódy ze cvičení, co jsme naprogramovali.<br/> 
- Také jsem si prošla oficiální Krita Scripting Book: https://scripting.krita.org/lessons/introduction.<br/> 
- Následně se hodilo také API Krity, kde jsem si mohla vyhledat různé variables pro třídy, například nodes.bounds(). https://api.kde.org/krita/html/classNode.html <br/>
- Také bylo využito chat gpt, ukázka:<br/>
Dotaz: <br/>
```
how do i look up if there is a group layer called a certain name?
```
Odpověď: <br/>
```
To check if a group layer with a specific name exists in the document, you can loop through the child nodes of the root node (or any other parent node) and check if a node matches the given name and is of the grouplayer type.

Here's a function to look up if a group layer with a certain name exists:

Function to Check for Group Layer by Name:
def find_group_by_name(self, parent_node, group_name):
    Search for a group layer with the specified name under the given parent node.
    Returns the group node if found, otherwise returns None.
    
    for node in parent_node.childNodes():
        if node.name() == group_name and node.type() == "grouplayer":
            return node
    return None

You can use this function to check if a group exists and create it if it doesn't.
