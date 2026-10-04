# CalcGPT 3 model installer 8 of 8. Run in order.
MODEL_ID=1282619148
BUILD=2
from ti_system import store_list,recall_list
FORMAT=13
ALPHABET="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~"
def decode(blob,length):
 out=[]
 for start in range(0,len(blob),5):
  value=0
  for ch in blob[start:start+5]: value=value*85+ALPHABET.index(ch)
  out.extend(((value>>24)&255,(value>>16)&255,(value>>8)&255,value&255))
 return out[:length]
def checksum(values):
 a=1; b=0
 for value in values:
  a=(a+value)%65521
  b=(b+a)%65521
 return (b<<16)|a
def installed(stage):
 try: marker=recall_list("tds"+str(stage))
 except Exception: return False
 return len(marker)>0 and int(marker[0])==MODEL_ID
def install(name,length,signed,blob,expect):
 values=decode(blob,length)
 if checksum(values)!=expect:
  print("Checksum failed for",name,"- re-paste this program"); raise SystemExit
 if signed:
  for j in range(len(values)):
   if values[j]>127: values[j]-=256
  pairs=[]
  for j in range(0,len(values),2):
   first=values[j]+128
   second=values[j+1]+128 if j+1<len(values) else 128
   pairs.append(first*256+second)
  values=pairs
 store_list(name,values)
 if len(recall_list(name))!=len(values):
  print("Verification failed for",name,"- re-paste this program"); raise SystemExit
def verify(prefix,count,length,expect):
 a=1; b=0; seen=0
 for part in range(count):
  for packed in recall_list(prefix+str(part)):
   packed=int(packed)
   for value in ((((packed>>8)-128)&255),(((packed&255)-128)&255)):
    if seen>=length: break
    a=(a+value)%65521
    b=(b+a)%65521
    seen+=1
 if seen!=length:
  print("Incomplete model part",prefix); raise SystemExit
 if (b<<16)|a!=expect:
  print("Corrupt model part",prefix); raise SystemExit

if installed(8):
 print("Part 8 of 8 already installed; skipping.")
 raise SystemExit
install('tda14',800,0,'7XJVnbO0uCs`~=~7XJWe-vAret4RX@t^WWovH&rRt4jj_7XJVnr~nw9t6T#B7XJVn)c_d6t7`)QCI0{+_y8#Qt8D`S7XJVkl>j4^t9Szd82<npy#N-ZtDpk_7XJVkdjK6~tR@2h7XJVn<N!FKtZoAU7XJVr@&Fjwtd0W!8~*?p@&F>{tdIi$7XJVnz5p1atw{p_7XJVn=Kv$Zt#1PW7XJVnzyKMVt%U;s7XJVnoB$_|t&sx&8UFwq^8hT{t_uSI82<nv;{YGyu1*60FaH1@qW~k2u3ZBF7XJVxssJ0Ju5SYXCI0{~?Eo0tu5beY7XJVnzW^Sru95=)8~*?nu>cr&uA2h@7XJV-bO0q`uA>707XJVnvj87}uHORy7XJVr`T<k-uH*v%7XJVkwE#L}uJ{808~*?n#sC?iuTKL2C;tE&tN<UMuU-QH9{&I(+5j<wuV4cJ8~*?n`T!Z-ud@RH7XJVnlmHlWulfT37XJVpssI^_up0vaG5-J-qW~Lxuv`NG7XJV<rT{3Eu~7p67XJVk?*JR+v2FtZ@&5pt=>Qqiv2z0e8~*?n?f@RVv6TY=7XJVn+yE!4vBm=c7XJWJssJ5)vFZZ=8~*?n+yEG^vQh&87XJVnnE*1GvS9-N7XJVn%m5g;vSR}P8~*?n$p9V6vV#Kv82<np>i{(CvXuh>7XJVpzW^SlvX=t@mj3`4z5q9tvZVt67XJVt*#H>XvZw<9E&l)(*Z?1vvc&@c82<nr>i`zevvmUiGXDS;@&F!_vzG$^7XJV;+W;Grv*ZH+7XJVlj{qBwv~~jk7XJV!p8zMHw3q_`7XJVldH@}Fw6X&L8UFwn<^UbWwPphV7XJVn-T)ZWwiyEeAO8Rr@c<&!wpIfG7XJVn>HsFOwr2wX7XJVn`T!x&ws->o8~*?n^Z+%#wyOgG7XJVnyZ{-6w#fqk7XJVrrvMq3w*UhG8~*?`!T=Vnw-EyX7XJWEp8zwHw@Cv47XJVvy#N@Vw|WBrCI0{x+yF70',1646988333)
install('tda15',800,0,'x0wR~8~*?n?*KKVx0?e17XJVq?*Jl)xH1C(7XJVkuK*jTxI+T~7XJVkt^gU5xSRt3C;tF9{{R-ZxV{4b7XJVn?EoF9xmN=K9sd9p+W;A?xn2VR7XJVn#{d|Qx>^GOIsX6_%>X5&x`zV*7XJVk#sC|=x`_h-GXDS@xBwQEyFdc~@&5pt*#JtsyKDmh8~*?q$^aI_yL|%y7XJVk_5dE2yW0Z*AO8Ry#{e<EyafXQ7XJVn^Z+`syc7cfIsX6__y8E>ye9(y7XJVp!vGn)ynX`!7XJVn?f@9lyz>J97XJVl^Z-Afy<GzU82<nk^Z+Q`z1#x;7XJVk?f^07z99nu8UFws+yE%TzLo<3C;tF9eE>9TzM=yF7XJVni~t>gzT^V{82<np<p3GnzU2b|7XJVkl>i@wzZU}l7XJVn>;OF3zh46Y82<oh^#CE#zpeuS7XJVqqW~L_zr_OpX#W5h`2ZH?zz_ofC;tEzmH;Agz&`^3C;tE#t^hQsz+eLa7XJV*n*bS>z}Eu+7XJVk$p9O?!KDKL7XJVn%m5vA!VCidl>Y!Y<NzqH!V?1k7XJV_%m5g|!W07l7XJVn<^UPl!gB)v7XJVn)BqT&!o&jr7XJVpuK*jb!x;kr7XJVl`2Zrk!-WF?7XJVtfB+kS!<GX8SN{MV$p9P4!>0oP82<np(*PF8#D)U^8~*?n{{R{8#h3#CME?L5*#H~a#i9cM9sd9<{{SEL#&-h%7XJVkp8y-1$7cfoM*ji2XaE>u$B6>~7XJVkqW~S8$J_$|82<nk=Kve3$UXxA9{&Iq@Bks!$Y=uq8~*?n!2lVq$aw<*7XJVn-~b}h$hiXm7XJVq&Hyfe$h`vq7XJWCp8yz_$l3z{7XJV_{{S1?$yx&dC;tE_<pBcR$*ThZ7XJVn-vAiO$|M5-8~*?q{{R^3%AErM8UFwq=l~ey%zXm@7XJVnssJ9D&20k!7XJWD=>Qv+&YuGS7XJVl(*PgH&!GbVDE|N@-vBSv&(#9}tp5NV',3367573060)
install('tda16',748,0,'=l~nZ&?W-_7XJVn+yFAd(2fHD7XJVqyZ{)y(FFql7XJVl;{X`Y(M1CQ7XJVkrT`nJ(VznWGXDUqh5#Fe(X|5r7XJVrtN<OK(&+;L8~*?p=l~hq(*pwmP5%HE;Q$!E({Td;8UFwn^Z*;v({lp=7XJVqt^g;K)1m_a7XJWf)Bq#D)TaXg7XJVn<^WUV)k^~a9{&Iq*#IG`)u;mi7XJVr>Hrw3*5d;J9{&Is%>W&~*qQ?X7XJVvl>i%+*t`P(7XJVk$p9v`*v$g~7XJVt@&GQ$*{cHp7XJV)&Hx$2+N}cs8UFwq^#B&*+P(t-7XJVp;{X`F+>HYOBmV#x^8gmy-UR~y9{&Is&H&TB-+u!D8~*?n=Kv+Y-;e_U8~*?v?f@O=-|_<h7XJVk#sD>k;Bo^17XJVny#N`6;D7@FRsR4M`~WAd;EMwQ7XJW0yZ{)y;E@9WRsR4dd;lVK;yMEW8~*?n)&Mt|;}Zh_7XJVk>Hr(x<URuc7XJVl!vGke<);Gx8~*?n)Bqlw=7s|RC;tE_!vG(y=ePp^9sd9s<^WZy=gR{C9{&It-vArb=$QimA^!jt;Q$`3>4^gX7XJZF?f@a{>Ounm7XJVn$^aO`>Tm-97XJWD<p3MY?9BrJE&l*0-vA=t?D7KujsE}^uK-1W?$QGQ7XJVn)BqTz@-qVfA^!j$@&Fm;^AZC9UH<^_^8lKz^Tq=J7XJV*i2x&s^jiY}7XJVk&j22p^l$?J9{&JJzW{Qk^<D!27XJVnx&SVp^`-*=C;tE_r~oB>_?-g)8~*?@=Kws<___lCGyeb{r2rP1`kDg(8~*?!+W;M)`pW|V7XJVnoB$tu`>X>18~*?n_5efF`^p0VGXDS;!2lbg`^*CX9{&Iq+5jw>`_2OZ7XJVncmO4E{ow-uAO8Ry_5c~u{=fqO7XJVkvH&8g|9S%e9{&Iqt^g;A',3953857026)
store_list("tds8",[MODEL_ID])

for stage in range(1,8):
 if not installed(stage):
  print("Missing model part",stage,"- run its installer"); raise SystemExit
verify("tdq0x",8,12800,3253446299)
verify("tdq1x",2,1800,935094154)
verify("tdq2x",2,2700,117706556)
verify("tdq3x",1,90,3996790513)
verify("tdq4x",1,90,1287334918)
verify("tdq5x",12,19200,72505880)
verify("tdq6x",1,640,3101615120)
store_list("tdlens",[12800, 1800, 2700, 90, 90, 19200, 640])
store_list("tdscale",[0.03368630747156819, 0.018995974007553942, 0.027542437155415694, 0.02038882097860021, 0.019929217541311668, 0.03322050515122301, 0.01716235678965651])
store_list("tdqp",[8, 2, 2, 1, 1, 12, 1])
store_list("tdinfo",[13,20,30,40,640,5,17,1282619148,BUILD])
print("CalcGPT 3 model installed and verified. Run tinylm.")
