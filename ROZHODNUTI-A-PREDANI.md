# Bomba: zadání a rozhodnutí z chatu

Tento dokument shrnuje podstatné požadavky a rozhodnutí z konverzace; nejde o doslovný přepis chatu. Úplné původní zadání je v souboru `PUVODNI-ZADANI.txt`. Při rozporu mají přednost pozdější změny popsané níže.

## Záměr a technické řešení

- Mobilní táborová hra s náhodnou dobou tikání a zvukem výbuchu, použitelná i s Bluetooth reproduktorem.
- Statická offline PWA bez serverové logiky, registrace, databáze, frameworků a externích knihoven. HTML, CSS a čistý JavaScript; zvuky a ikony jsou lokální.
- Výchozí interval je 30 až 90 sekund. Nastavení se ukládá lokálně; čas je volitelný a při vypnutí se nesmí prozradit průběhem.
- K dispozici jsou START, ZASTAVIT a samostatné testy zvuků. Zvuky generuje `generate_audio.py` pomocí standardní knihovny Pythonu.

## Pozdější změny vzhledu a ovládání

- Mobilní rozhraní má být kompaktní. Minimum a maximum jsou vedle sebe, velký obrázek byl odstraněn a malá ikona bomby vrácena do záhlaví. Popis pod nadpisem byl odstraněn.
- Návod na přidání aplikace na plochu je pod testy zvuků.
- Pozdější požadavek změnil původní pravidlo pro ruční výbuch: tlačítko se má objevit ihned po zaškrtnutí volby a má fungovat i mimo probíhající kolo. Při běžícím kole jej ukončí výbuchem.
- Po výbuchu má stav `Výbuch!` zůstat 5 sekund nebo do dalšího ovládání a poté se vrátit na `Připraveno`.
- Výbuch byl několikrát zesílen a přegenerován; skutečná hlasitost závisí také na telefonu a reproduktoru.

## Publikování a aktualizace

- GitHub Pages může publikovat soubory z veřejného repozitáře. `index.html` musí být v kořeni publikační složky; ZIP je potřeba nejprve rozbalit a nahrát jeho obsah se zachováním složky `assets`.
- U domény `www.vcas-os.cz` už existuje webhosting. DNS nerozlišuje cestu `/bomba`: pro `www.vcas-os.cz/bomba` lze aplikaci nahrát do podadresáře stávajícího hostingu nebo tam nastavit proxy. Alternativou je samostatná subdoména směrovaná na GitHub Pages. Před změnou DNS je nutné zohlednit stávající web a služby.
- Service worker používá cache-first a označení `bomba-v1`. Při publikování změn je třeba změnit verzi cache v `service-worker.js`, jinak se uživatelům může zobrazovat stará verze. Po nasazení může být potřeba stránku znovu načíst; výjimečně smazat data webu nebo znovu nainstalovat PWA.

## Ověření a omezení

- V předchozí práci byly vygenerovány WAV a ikony a ověřeno lokální HTTP načtení a metadata zvuků. Automatizovaný test prohlížeče tehdy selhal kvůli prostředí; plnou funkčnost v mobilním prohlížeči, offline režim a Bluetooth je nutné ověřit na zařízení.
- Mobilní systém může na pozadí pozastavit zvuk nebo časovače. Během hry je vhodné ponechat aplikaci v popředí a vyzkoušet hlasitost předem.
- Postup místního spuštění, instalace a nasazení je také v `README.md`. Původní README a zadání mohou obsahovat starší požadavky, které byly později změněny v chatu.
