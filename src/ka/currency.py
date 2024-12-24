"""
Contains utilities for scraping currency exchange rates.
"""

import datetime
import argparse
import os.path
import sys

import ka.config
from .config import ConfigProperties

SCRAPE_URL = "https://www.xe.com/currencytables/?from=USD&date=${date}"

def scrape_exchange_rates():
    from bs4 import BeautifulSoup
    import requests
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    r = requests.get(SCRAPE_URL.format(date=yesterday))
    soup = BeautifulSoup(r.content, "lxml")
    table = soup.find("table")
    rows = table.find_all("tr")
    return list(filter(lambda d: d is not None,
                       [parse_row(row) for row in rows]))

def parse_row(row):
    symbol = row.find("th")
    if not symbol:
        return None
    symbol = symbol.text.strip().lower()
    datums = [td.text.strip() for td in row.find_all("td")]
    if len(datums) >= 3:
        return CurrencyData(symbol,
                            "".join(datums[0].lower().split(" ")),
                            float(datums[1]))
    return None

class CurrencyData:
    def __init__(self, symbol, name, dollar_rate):
        self.symbol = symbol
        self.name = name
        self.dollar_rate = dollar_rate

    def __str__(self):
        return f"Currency[symbol='{self.symbol}', name='{self.name}', rate={self.dollar_rate}]"

    def __repr__(self):
        return str(self)

def scrape_and_store_rates_to(path):
    currencies = scrape_exchange_rates()
    with open(path, "w") as f:
        for c in currencies:
            f.write(",".join([c.symbol, c.name, str(c.dollar_rate)]))
            f.write("\n")

DEFAULT_CURRENCY_DATA = """usd,usdollar,1.0
eur,euro,0.9613451479177936
gbp,britishpound,0.7980882123146935
inr,indianrupee,85.11416418044818
aud,australiandollar,1.6033769369291266
cad,canadiandollar,1.4380462361224067
sgd,singaporedollar,1.3570340775388345
chf,swissfranc,0.8987035037503758
myr,malaysianringgit,4.488402697733426
jpy,japaneseyen,157.2281737816283
cny,chineseyuanrenminbi,7.298265168786153
nzd,newzealanddollar,1.77281623912258
thb,thaibaht,34.23290943801689
huf,hungarianforint,396.96449762002607
aed,emiratidirham,3.6725
hkd,hongkongdollar,7.769872643185045
mxn,mexicanpeso,20.195988772504975
zar,southafricanrand,18.55936191539975
php,philippinepeso,58.55392195785541
sek,swedishkrona,11.045870538177457
idr,indonesianrupiah,16149.82614394941
brl,brazilianreal,6.194233457018404
sar,saudiarabianriyal,3.75
try,turkishlira,35.267920009494844
kes,kenyanshilling,129.3584071654276
krw,southkoreanwon,1453.1808538234131
egp,egyptianpound,51.0826643062161
iqd,iraqidinar,1309.1277338322443
nok,norwegiankrone,11.363675084010929
kwd,kuwaitidinar,0.30823001590559257
rub,russianruble,101.22349837742166
dkk,danishkrone,7.172343866484728
pkr,pakistanirupee,278.2564105477408
ils,israelishekel,3.6639471848088334
pln,polishzloty,4.101292038048025
qar,qataririyal,3.64
xau,goldounce,0.0003822363914263758
omr,omanirial,0.3850160778975956
cop,colombianpeso,4432.21925797807
clp,chileanpeso,990.4669917555323
twd,taiwannewdollar,32.692710992080244
ars,argentinepeso,1025.7818135627203
czk,czechkoruna,24.151454387829308
vnd,vietnamesedong,25464.29645553592
mad,moroccandirham,10.059779711928606
jod,jordaniandinar,0.709
bhd,bahrainidinar,0.376
xof,cfafranc,630.6010791927121
lkr,srilankanrupee,295.2545084145073
uah,ukrainianhryvnia,41.64399227329809
ngn,nigeriannaira,1548.3564483875398
tnd,tunisiandinar,3.1872873783296884
ugx,ugandanshilling,3671.2209722267735
ron,romanianleu,4.784069303357981
bdt,bangladeshitaka,119.48181837473881
pen,peruviansol,3.7513991616971083
gel,georgianlari,2.804696675146796
xaf,centralafricancfafrancbeac,630.6010791927121
fjd,fijiandollar,2.3368123097871973
vef,venezuelanbolívar,5157548.360942523
ves,venezuelanbolívar,51.575483609425234
byn,belarusianruble,3.2700036373693013
uzs,uzbekistanisom,12837.150865242415
bgn,bulgarianlev,1.8802276806520581
dzd,algeriandinar,134.88453503135926
irr,iranianrial,42088.4978710354
dop,dominicanpeso,60.733002146430636
isk,icelandickrona,139.4980247114502
crc,costaricancolon,506.1263723698668
xag,silverounce,0.033678971783355195
syp,syrianpound,13001.830115838879
jmd,jamaicandollar,156.17867422107298
lyd,libyandinar,4.895772861258207
ghs,ghanaiancedi,14.698221889116137
mur,mauritianrupee,46.856369026050935
aoa,angolankwanza,924.6935437818297
uyu,uruguayanpeso,44.510228975693636
afn,afghanafghani,70.12195914117902
lbp,lebanesepound,89538.34608619954
xpf,cfpfranc,114.71899139788485
ttd,trinidadiandollar,6.790766700101594
tzs,tanzanianshilling,2405.7843358730033
all,albanianlek,93.31985751914802
xcd,eastcaribbeandollar,2.706293490936114
gtq,guatemalanquetzal,7.697536351511069
npr,nepaleserupee,136.24649831185243
bob,bolivianbolíviano,6.89441445497846
zwd,zimbabweandollar,361.9
bbd,barbadianorbajandollar,2.0
cuc,cubanconvertiblepeso,1.0
lak,laokip,21885.79541549342
bnd,bruneiandollar,1.3570340775388345
bwp,botswanapula,13.783815738308604
hnl,honduranlempira,25.374638701515952
pyg,paraguayanguarani,7813.815980070785
etb,ethiopianbirr,126.86652903247133
nad,namibiandollar,18.55936191539975
pgk,papuanewguineankina,4.051886556979464
sdg,sudanesepound,601.4746841446706
mop,macaupataca,8.002968822480597
bmd,bermudiandollar,1.0
nio,nicaraguancordoba,36.765458835832774
bam,bosnianconvertiblemark,1.8802276806520581
kzt,kazakhstanitenge,521.8543049881133
pab,panamanianbalboa,1.0
gyd,guyanesedollar,208.41487947516498
yer,yemenirial,249.91548006898086
mga,malagasyariary,4703.518879107322
kyd,caymaniandollar,0.8269531733378046
mzn,mozambicanmetical,63.907638001877935
rsd,serbiandinar,112.46887905460912
scr,seychelloisrupee,13.93765212431303
amd,armeniandram,395.58651780582125
azn,azerbaijanmanat,1.6999870703362865
sbd,solomonislanderdollar,8.39826559488352
sll,sierraleoneanleone,22749.721446401792
top,tonganpa'anga,2.403755729447125
bzd,belizeandollar,2.0121306760212936
gmd,gambiandalasi,72.2745961211744
mwk,malawiankwacha,1733.3924961260363
bif,burundianfranc,2955.2368806277645
htg,haitiangourde,130.60828813166603
sos,somalishilling,567.9513756423538
gnf,guineanfranc,8638.869148788152
mnt,mongoliantughrik,3434.654998117644
mvr,maldivianrufiyaa,15.439188434212555
cdf,congolesefranc,2844.9996323352575
stn,saotomeandobra,23.570555463369566
tjs,tajikistanisomoni,10.93724862929427
kpw,northkoreanwon,900.0166091384315
kgs,kyrgyzstanisom,86.799979858638
lrd,liberiandollar,180.76029360264545
lsl,basotholoti,18.55936191539975
mmk,burmesekyat,2098.2667267865095
gip,gibraltarpound,0.7980882123146935
xpt,platinumounce,0.0010610015013641607
mdl,moldovanleu,18.357110141479957
cup,cubanpeso,23.951291384657566
khr,cambodianriel,4012.6648532975273
mkd,macedoniandenar,59.14322176136583
vuv,ni-vanuatuvatu,120.97534901963675
ang,dutchguilder,1.798137302382223
mru,mauritanianouguiya,39.6945043051644
szl,swazililangeni,18.55936191539975
cve,capeverdeanescudo,106.0075294608951
srd,surinamesedollar,35.51792198698714
svc,salvadorancolon,8.75
xpd,palladiumounce,0.0010700895621035828
bsd,bahamiandollar,1.0
xdr,imfspecialdrawingrights,0.7668258903439369
rwf,rwandanfranc,1387.971039230261
awg,arubanordutchguilder,1.79
btn,bhutanesengultrum,85.11416418044818
djf,djiboutianfranc,177.93029369167797
kmf,comorianfranc,472.95080939453413
ern,eritreannakfa,15.0
fkp,falklandislandpound,0.7980882123146935
shp,sainthelenianpound,0.7980882123146935
spl,seborganluigino,0.166666666
wst,samoantala,2.8070593712299603
jep,jerseypound,0.7980882123146935
tmt,turkmenistanimanat,3.5089425400682126
ggp,guernseypound,0.7980882123146935
imp,isleofmanpound,0.7980882123146935
tvd,tuvaluandollar,1.6033769369291266
zmw,zambiankwacha,27.719440906454164
ada,cardano,1.160340696642952
bch,bitcoincash,0.0021802529728369114
btc,bitcoin,1.080078396710183e-05
clf,clf,0.02579803062984011
cnh,chineseyuanrenminbioffshore,7.3070795199910155
doge,dogecoin,3.0978011081942727
dot,polkadot,0.1367952062270505
eth,ethereum,0.00029355513695854225
link,chainlink,0.04138871918935862
ltc,litecoin,0.009436622091366803
luna,terra,2.340686910595697
mxv,mxv,2.4138045263439705
sle,sierraleoneanleone,22.749721446401793
uni,uniswap,0.07052494164864277
ved,ved,51.575483609425234
xbt,xbt,1.080078396710183e-05
xlm,stellarlumen,2.714797320512724
xrp,ripple,0.4445053185451475
zwg,zimbabweandollar,25.476912238244978"""

def load_currency_data():
    path = ka.config.get(ConfigProperties.CURRENCY_PATH)
    data = None
    if os.path.exists(path):
        try:
            with open(path) as f:
                data = parse_currency_data(f.read())
        except Exception:
            print("Failed to parse currency data, falling back to default...",
                  out=sys.stderr)
    if data is None:
        # Fall back to the default.
        data = parse_currency_data(DEFAULT_CURRENCY_DATA)
    return data

def parse_currency_data(s):
    cs = map(lambda line: line.split(","), s.split("\n"))
    result = []
    for c in cs:
        if len(c) < 3:
            return None
        result.append(CurrencyData(c[0], c[1], float(c[2])))
    return result
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save-path", required=True)
    args = parser.parse_args()
    scrape_and_store_rates(args.path)
