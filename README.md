# SmartLock
![20240124_183954](https://github.com/vukasinb7/Smart-Lock/assets/51921035/a50f6589-2bef-476e-9a25-5261436b4ac3)

## RFID Unlock
https://github.com/vukasinb7/Smart-Lock/assets/51921035/39936019-b7f6-4677-b1db-a3396ef2b5e7

## Pin Unlock
https://github.com/vukasinb7/Smart-Lock/assets/51921035/6db37615-96e7-4641-a52c-213ec19f2875

## Change Pin
https://github.com/vukasinb7/Smart-Lock/assets/51921035/9ae02323-b954-4454-9a6c-9dadcb5a535c

## Add New Face
https://github.com/vukasinb7/Smart-Lock/assets/51921035/89f61633-000a-4b69-88e4-db1149f8da9b

## Face Recognition
https://github.com/vukasinb7/Smart-Lock/assets/51921035/14e8de73-c724-4877-ab06-3ad2226fe69c

## Face Recognition Dark Mode
https://github.com/vukasinb7/Smart-Lock/assets/51921035/0f65f87c-7333-4b1f-ba6f-4f22c13cde54

## Alarm
https://github.com/vukasinb7/Smart-Lock/assets/51921035/a5415788-063d-4e4b-bac8-c0de92248742





## Opis Problema
Naš cilj je kreirati inovativan i siguran softver za pametnu kontrolu vrata koji će se izvoditi na Raspberry Pi Pico uređaju uz pomoć ESP 8266 mikrokontrolera za konekciju sa internetom, u microPython programskom jeziku. Ovaj softver će omogućiti različite metode otključavanja vrata, uključujući:

1. RFID - Potrebno je podržati otključavanje vrata putem RFID tehnologije. Svaki autorizovani korisnik će imati svoju RFID karticu ili tag koji će se koristiti za verifikaciju.

2. PIN kod - Potrebno je implementirati otključavanje vrata putem PIN koda. Korisnicima će biti omogućeno unošenje odgovarajućeg PIN koda na tastaturi ili ekranu kako bi se vrata otključala.

3. Detekciju lica (opciono) - Softver će biti sposoban za prepoznavanje lica korisnika kao jedan od načina za otključavanje vrata. Za ovu svrhu koristićemo kamere za prepoznavanje lica.

Naš softver će uključivati zaštitne mehanizme kako bi se osigurala sigurnost sistema. Na primer, ako se tri puta unese netačan PIN kod, aktiviraće se zvučni alarm uz pomoć buzzera koji će upozoriti na potencijalnu neovlašćenu aktivnost i istovremeno će kamera uslikati osobu koja je neovlašćeno pokušala da uđe u zgradu. Takođe će biti implementirane dodatne sigurnosne funkcije, kao što su praćenje i evidencija svih pokušaja otključavanja vrata i obaveštenja vlasnika u slučaju sumnjive aktivnosti i izmena pin koda.
Potrebno je implementirati prikaz stanja i jednostavan meni vrata uz pomoć displeja. 
Sistem će biti aktivan samo ukoliko senzor blizine detektuje da se osoba nalazi ispred vrata i tek tada će kamera uslikati korisnika i poslati sliku na server koji će izvršiti prepoznavanje lica.

Ovaj softver će omogućiti visok nivo sigurnosti i funkcionalnosti za kontrolu pristupa i otključavanje vrata.




