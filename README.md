# Sunrise AAC

**It shouldn't cost $7,000 to say "Good morning".**

**Version**: 0.4.0

Sunrise AAC is an open-source, lightweight AAC (Augmentative and Alternative Communication) desktop application, built to bring back user autonomy. Powered by Python and Pygame, Sunrise AAC replaces expensive, locked-down speech devices with an intuitive interface that anyone can configure in 30 seconds, just one right click away.

Distributed freely under the GNU General Public License, version 3 (GPLv3 or later). 

## But Why?

Traditional AAC companies charge upwards of $7,000-8,000 for "rugged" devices. Truthfully, these are nothing more than locked-down standard consumer tablets wrapped in thick plastic and big speakers. The price is artificially inflated only because these companies' products are covered by medical insurance. If you have government funding, like the NDIS (National Disability Insurance Scheme) in Australia, you wait weeks or months for approval. **If you don't have funding, you are priced out of communication.**

Dedicated proprietary AAC devices are also built on a fragile, closed lifecycle. When a device breaks,
 these companies often just send over a whole new device entirely, while the other one just becomes e-waste. This is a problem with a lot of technology but the locked-down software makes it worse.

I have a sister who uses an AAC talker device. This project started because I took one look at the price, and said "that's outrageous". The modern human species, *Homo sapiens* has been around for 200,000 years. Social communication is baked into our biology. It is what allowed us to survive in tribes, share technologies, tell stories. And today, communication is more important than ever before, in our ever-more-connected world. A speech or language impairment does not take away from a human being their need nor fundamental right to communicate with others. The fact that a modern human voice can be locked behind a $7,000-8,000 paywall is an unacceptable tragedy. Sunrise AAC exists to restore the power of speech to those of which it has been deprived for too long, and to provide an intuitive, open alternative for those who feel that the corporations have gone too far.

Even beyond the communication devices themselves, commercial AAC apps trap you into using proprietary symbol sets (like SymbolStix or Tobii Dynavox) that carry heavy licensing fees and strict distribution restrictions. 

To ensure this project stays completely free, **all image icons in this project are hand-drawn and licenced under Creative Commons Attribution-ShareAlike 4.0** (see Licence section for details). No monopolies allowed here.

You can even add your own. With LiveEdit, modifying a button is simple as a right-click. Just drop an image into `assets/images`, right-click, and you have a new button in 30 seconds. 

The corporations thought they could get away with a paywall on human speech. What might they come for next? If proprietary soiftware s allowed to proliferate unchecked, the next generation will inherit a world where they have no rights. Such a future cannot happen.

## Project Status

Currently in development. Features may or may not work, or be incomplete.

## Requirements

- Python 3.x (tested on 3.14.0, older versions may or may not work)
- For further dependencies, run: `pip install -r requirements.txt`

## Licence

This project uses mixed-scope licencing to ensure it stays open-source and free for everyone, while preventing corporate exploitation:
- **Software**: All Python source code and JSON configurations are licensed under the **GNU General Public Licence v3 (GPLv3)** or later. See [LICENCE](./LICENCE) for the GNU GPLv3 licence terms.
- **Icons**: All hand-drawn image icons inside the `assets/images` directory are licenced under the **Creative Commons Attribution-ShareAlike (CC-BY-SA) 4.0**. The licence file can be found inside that directory. See the corresponding [LICENCE](./assets/images/LICENCE) for the licence terms.
- **Fonts**: This project uses fonts licensed under the **SIL Open Font Licence v1.1**. These fonts are available on Google Fonts as follows:
  - Atkinson-Hyperlegible: https://fonts.google.com/specimen/Atkinson+Hyperlegible
  - ComicNeue-Bold: https://fonts.google.com/specimen/Comic+Neue
  - Additionally, a copy of the SIL OFL v1.1 is available at: [LICENCE](./assets/fonts/LICENCE)
