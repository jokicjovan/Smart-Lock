# SmartLock
## Opis Problema
Naš cilj je kreirati inovativan i siguran softver za pametnu kontrolu vrata koji će se izvoditi na Raspberry Pi Pico uređaju uz pomoć ESP 8266 mikrokontrolera za konekciju sa internetom, u microPython programskom jeziku. Ovaj softver će omogućiti različite metode otključavanja vrata, uključujući:

1. RFID - Potrebno je podržati otključavanje vrata putem RFID tehnologije. Svaki autorizovani korisnik će imati svoju RFID karticu ili tag koji će se koristiti za verifikaciju.

2. PIN kod - Potrebno je implementirati otključavanje vrata putem PIN koda. Korisnicima će biti omogućeno unošenje odgovarajućeg PIN koda na tastaturi ili ekranu kako bi se vrata otključala.

3. Detekciju lica (opciono) - Softver će biti sposoban za prepoznavanje lica korisnika kao jedan od načina za otključavanje vrata. Za ovu svrhu koristićemo kamere za prepoznavanje lica.

Naš softver će uključivati zaštitne mehanizme kako bi se osigurala sigurnost sistema. Na primer, ako se tri puta unese netačan PIN kod, aktiviraće se zvučni alarm uz pomoć buzzera koji će upozoriti na potencijalnu neovlašćenu aktivnost i istovremeno će kamera uslikati osobu koja je neovlašćeno pokušala da uđe u zgradu. Takođe će biti implementirane dodatne sigurnosne funkcije, kao što su praćenje i evidencija svih pokušaja otključavanja vrata i obaveštenja vlasnika u slučaju sumnjive aktivnosti i izmena pin koda.
Potrebno je implementirati prikaz stanja i jednostavan meni vrata uz pomoć displeja. 
Sistem će biti aktivan samo ukoliko senzor blizine detektuje da se osoba nalazi ispred vrata i tek tada će kamera uslikati korisnika i poslati sliku na server koji će izvršiti prepoznavanje lica.

Ovaj softver će omogućiti visok nivo sigurnosti i funkcionalnosti za kontrolu pristupa i otključavanje vrata.




