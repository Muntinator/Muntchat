# CalcGPT 3 model installer 7 of 8. Run in order.
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

if installed(7):
 print("Part 7 of 8 already installed; skipping.")
 raise SystemExit
install('tda5',800,0,'7XJWJ`T!fK0b~OJ7XJVn-vCVC0c8UK82<oD)Bq>O0cHaL8~*?n{{SN70cQgM7XJVkrT`nJ0cZmNM*jd7-vA@j0cisOIR5}U{{S@f0cryP7XJVn-T)Y_0c!&Q7XJV!>i`|t0c-;R9sd9u^8gv>0c`^TZT|op`2ZN%0d4~T8~*?n&j2Ey0dE5UBL4t3y8&;z0dNBV82<nn{{S200dWHW7XJVqv;Y{D0dfNX8~*?p@BkL#0doTY8~*?nu>c*M0dxZZCI10*%>Wpt0d)fa8~*?njQ}2v0d@lb8~*?p)&L#70e1rc7XJVq(f~Jt0eAxdjsE~HqW~L@0eJ%e8~*?n-~b=V0eS-f7XJVndjJ`G0eb@gDE|N!_5d5>0ek}h9{&Iqr~oI30eu4i8UF!&>i{R~0e%Aj7XJVn*8zU70e=Gk8~*?pp#T<^0e}Ml7XJWClmHu)0f7Sm7XJZ(%m5v-0fGYn8~*?q;{YAc0fPeoIsX6_;s6=W0fYkp7XJVqtN<s90fhqqBL4su{{S2H0fqwr7XJVl{{ScS0fz$s7XJVr<^UVa0f++t8~*?p!~iI<0f_?viT?l?q5u|o0g3|v7XJVnf&e0Y0gD3w7XJVneE?E;0gM9xC;tEz&Hx_B0gVFy7XJVx_y94Z0geLz7XJZ`h5#6O0gnR!7XJVr&H!wr0gwX#9{&Iz^#B;e0g(d$8UFwl(*PUO0g?j%7XJVx^#C9B0h0p&8~*?n&Hy>R0h9v(82<n#-vA%q0hI#)7XJVnqW~y}0hR**L;nCJ{{TMr0ha>+AO8WDod6q&0hj{-82<nk!T=k&0ht2<ng0M5xd0o60h$8<KK}q1<NzV$0h<E=9sd9rqW~6`0h|K>82<nz@BlC10i6Q?8~*?n{{R{10iFW@IR5|}<^U+>0iOc^7XJVk{{S1-0iXi_7XJVzwE!Nl0igo`C;tEz%m5h70ipu{7XJVnlK@DI0iy!|8~*?q_5c>r0i*)}8~*?nx&Rou0i^>0rT+jso&Xkw',340257227)
install('tda6',800,0,'0j2{07XJVn_5dEt0jC218UFwl;Q$z=0jL8282<nk@Bk;+0jUE37XJVrq5v$D0jdK47XJVx%m5p*0jmQ57XJVkqW~M70jvW67XJaPr~n(80j&c77XJVnngAV!0j>i882<nk<NzVk0j~o9X#W5qrvOb|0k8uA8~*?u(Et|F0kH!B7XJVtzW^Dy0kQ)C7XJVkuK*&S0kZ=D7XJVn{{SiT0ki`E9{&Iv;{YYu0ks1F8UFwn_5dgB0k#7G8~*?$>i`++0k;DH7XJVk&;TXS0k{JI9{&IvjsO;b0l5PJ7XJV<y#Oeb0lEVLy8i$;LIF)F0lNbL82<np-T)b`0lWhM7XJVk*Z>`;0lfnN8UFwl{{S7?0lotO7XJWs>;M?!0lxzP7XJV_y#N@!0l)(Q82<nt%>Wjh0l@<R8~*?n&Hxys0m1_S{Qm$U*Z?Ki0mB0T8UFwx$^b*Z0mK6U7XJVkvj7{j0mTCV7XJVp%m5j}0mcIW7XJVlssJ0C0mlOX7XJaqzW^SY0muUY7XJVkumB#70m%aZH~#_2<^Vh90m=ga7XJVnf&d?J0m}mb7XJau_5dBj0n7sc9{&N%>Hr<T0nGye&Hn&Cxd8mR0nP&e7XJW5!T=b!0nY;f7XJay_5dcf0nh^g7XJVqtN<II0nq~h7XJVk!T>O%0n!5i82<ns@&F&T0n-Bj8~*?p(*PF80n`Hk7XJVn^Z*^P0o4Nl7XJVq;s6`O0oDTm7XJVr(*PLC0oMZn8~*?p>i`|%0oVfp*#7{M%m5g+0oelp7XJVp^8g~}0onrq8~*?n+W;uG0owxr8~*?n^8g>w0o(%s7XJVny#Oqv0o?-t7XJVnumB>b0p0@u7XJVruK*jU0p9}v8~*?n#Q+|;0pJ4w7XJVk#Q+<{0pSAx82<nk;{YL{0pbGy7XJVr$pPZQ0pkMz8~*?n;{X`O0ptS!7XJVnaR4`90p$Y#7XJVn$N)yX0p<e$8~*?p%m5a`0p|k%8~*?n>Hrwj0q6q&7XJV_',989854521)
install('tda7',800,0,'p8zL^0qFw(X#W5-qW~D00qO$)7XJVnrvMp*0qX+*M*jd9@&F;(0qg?+9{&Iq%m62%0qp|-9sd9r(*PE{0qz3;AO8Rt$p9Xz0q+9<7XJVquK*pH0q_F=7XJVnvj7;80r3L>7XJVq-T)iC0rCR?7XJVn*Z@0|0rLX@9{&Iz)BqvI0rUd^7XJVr+W;M&0rdj_82<np^Z*vW0rmp`8~*?-{{R-^0rvv{7XJVnqyQa^0r&#|DE|N!uK*>W0r>*}8~*?&@&Fd*0r~>~7XJV<<^Ue%0s8|08~*?u{{R-!0sI317XJVn{{T1N0sR928~*?@o&X<}0saF37XJVq-2fes0sjL4A^!jt{{SBH0ssR57XJVq^8gsz0s#X68~*?-i~<3K0s{j88UFws@&Fs=0t5p97XJVn)&Ll|0tEvC1^)md{{S1#0tN#B9{&Iq{{S1~0tW*C7XJVl+W;Gq0tf>F2>$>U^#B{f0to{E7XJVn+yEK50ty2F8UFwx*Z>>O0t*8G82<n#(*POB0t^EJ4F3Qd;s6-B0u2KI7XJVq*Z>&L0uBQJ9{&It@&Fyz0uKWK7XJVy{{SNY0uTcLC;tE#^8g;`0uciM9{&Iq{{SKX0uloN7XJVntpFW~0uuuO9{&It@BkL@0u%!P8~*?n=>Ra(0u=)QC;tE?$^a<J0u}=R7XJVn-vAwo0v7`U7ykem)&Ll-0vH1T82<nzt^gvg0vQ7U7XJVp=l~nJ0vZDV7XJVq;{Y4f0viJY8~*?nwg4!$0vrPX8~*|v%m5v~0v!VYTmJwe?Eo9?0v-bZCjS5*k^mc$0v`hcAO8Rr!vG$c0w4nbC;tE}?f^9I0wDtcAO8R+?*KXP0wMzd82<nr>;M+y0wV(eX#W5f#sC|}0we<f7XJVlp8y+q0wn_g7XJV?zW^Sp0wx0h7XJVrmH-%V0w)6i7XJV_*#H@`0w@CjC;tE+r2rwN0x1Ik7XJV(^#B=@0xAOl8~*?wwg4Ea0xJUm82<nk^Z*;N0xSan',979557548)
install('tda8',800,0,'9sdF>?*Jjs0xbgo7XJVnu>cvS0xkmp7XJVk^a3vG0xtsq8~*?u=mIa?0x$yr8~*?v{{R;M0x<&sDE|N($pC1{0x|;t7XJVk)&L*40y6^u7XJVkyZ{}A0yF~v7XJVn+yEG^0yP5w7XJVncK{h~0yYBx7XJVn{{S7#0yhHy7XJVn*#H=(0yqNz7XJVp#sC?i0yzT!C;tE&fB-ar0y+Z#7XJVr+W;)K0y_f$7XJVrvH%#e0z3l%7XJb~VE`FV0zCr&7XJVqrvMwB0zLx(7XJVqw*o$R0zU%)7XJVln*b${0zd-*7XJVn^8!G*0zm@+8UFws*8mv20zv}-7XJVpwg4NR0z(4;8~*@B;{X=p0z?A<8~*?uvH%vQ0!0G=82<nx@&Ft10!9M>82<uB!T=ts0!IS?7XJVk^8g>`0!RY@H~#<@*aAq-0!ae^M*je8{{U{u0!jk_7XJVkxBw-p0!sq`8~*?q{{R;M0!#w{7XJVnwg5D$0!;$|AO8R}@&Fy=0!{+}7XJVnxBxw)0#5?~8~*?n;Q$@O0#E}07XJV;fB;NU0#O419sd9p{{S1Z0#XA2A^!jw@BkL!0#gG38UFwl@&Ft10#pM4P5%HM*8m;70#yS582<nk{{Tbd0#*Y682<nk>i`?A0#^e7AO8Rr@c<jR0$2k87XJVkssJ0J0$BqBS^oeS#Q+wZ0$KwA7XJcT?*JIz0$T$B8UFwn<N{mQ0$c+ET>k({<Nz420$l?D9{&Is;Q&kF0$u|E8~*?nxd0it0$&3F7XJVn@&Fyz0$>9G7XJVz(*P!>0$~FJVgCRYssJdE0%8LI9sd9sxd0xy0%HRJ7XJVuwg4=)0%QXK7XJVr@&F;`0%ZdL9{&Pmu>c*h0%ijM7XJVp{{SM+0%rpNA^!j!@c<&!0%!vO9sd9u-2fQO0%-#P7XJVn(f}T`0%`*Q8~*}o{{R-U0&4>R7XJVufB+tV0&D{S7XJVk{{S2R0&N2T7XJVqzW^Jb0&W8U82<n#!vIaR',2910837267)
install('tda9',800,0,'0&fEV7XJVn{{fl80&oKW8~*?qzW^e?0&xQX7XJVqnE)qu0&)WY7XJcrVgMOp0&@cZ8~*?p{{R-_0(1ia7XJVk{{R`o0(Aob7XJVk#sC?(0(Juc8~*?n{{S7C0(S!d8~*?n%m66N0(b)e7XJVq?*JIz0(k=f82<nk!vH&$0(t`g8~*?n{{SBU0(%1h7XJVntpFH$0(=7i8~*?p+W;B10(}Dj82<nr{{R-)0)7Jk82<nn%m5#|0)GPl8~*}-{{R;7fwBVt8~*?n;s6-Egy;hR7XJVnzW^DMhmHdP7XJVn+yFAuh%EyE82<nn%>W_4h>HUN82<nk+yEWZh`s{=7XJVn!2lS#ij4yR8~*?n>i|Kmi|+#f7XJVnwE!KejR6Ay7XJV<WB?~qjidtr9{&Is>HrqXj++Aj7XJV=ssN#bl0yRk7XJVty8sxwl2ii#7XJVny#N`2l4Sz`7XJVn@Bkyzl6C_CC;tE&<Nzh!l7|BT7XJVnc>pJClBoj#C;tE#;{X<zlDY!`7XJVq*Z>*DlMe#`9{&Iqj{q2UlOO{C7XJVr$p9tElQ9DT7XJVk)BtF_lQRPV8~*?{(EugUlT!l#7XJVn<p3G2lT`x%8~*?n=KvqVlV$?|7XJVl@&Fj}lXn9EA^!jytpFI3ld1y%82<nk%K#y(leq%`DE|N!>;NZ(le+@|AO8R))c`2dlk5WkIsX7B{{SfAlr#eX8~*?n_5dZbltlvo7XJVn!vGzPlvD!%8~*?n=l~+vlvV=(7XJVljQ|*XlxG6~8~*?n)c_rol$HYk7XJV>(*PT<l$rwo7XJVn!~h<zl)3`|7XJVl;Q%Pul+6PG7XJVn`v4uvl-dIT8~*?n=m2QRl->gX8~*?p$N(0<l<NZk7XJVnw*VNTl<xxo7XJVn&Hx^?l??*`8~*?n+yEuTl@S8~8~*?v*Z>yKl^z2C7XJVztpFIUl_CQG7XJVr+5i~Tl`{hX82<nt)&Lg8l{EtZ7XJVkqW~R?l|TakKmPz5',2550594524)
install('tda10',800,0,'_5c~}l~)4*7XJVn!2lSmm2(3C7XJVqtN<8>m3adI8~*?n?Eo0Lm5KuZ7XJVlfB+kNm6Zbk7XJVk>Hr?dm6rnm7XJVn>;M_Rm8=5*82<npp#T<;mA3-`7XJVq$^b^ZmAwN17XJVk?*JR!mD>XVIsX6_&;S^>mFfck7XJVk<^W0HmFxom7XJVqzyKS*mHPt#7XJWS{{U6?mHz_(8~*?n&Hy5<mJR~|8~*?p;{ZI}mLCHE7XJVn)BqjCmM#MUP5%HEm;fb`mO%pm7XJVl;{X`JmPG>q8~*?n>;NUdmPZ2s7XJVp(EuBKmQn)%7XJVn_5dB&mSY0|7XJVkt^gUTmS+P182<nr?*JC>mT3b37XJVp;{YDnmUIIEA^!jy>HtE|mWcxZ82<nv{{R-_mXrekQ~v-j!2lR=mYM?q7XJVkr2rX+mbL=`7XJVz{{SMVmbe1|C;tEz^#C8emd67C8UFwsyZ{)cmd^tK8~*?n`2Zcvmg@rm8UFws%m5p|mhS@q7XJVn-T)rFmhl4s8~*?n^Z*^qmihw#7XJVn`T$w_mlFd37XJVl$p9U}mmUKE82<nk)Bqodmm~uKH2(k=$^aX?mq-Hu7XJVn!vGkbmtX?`8~*?npa2<;mudq57XJVkhX5OZmwN*M7XJVkX8<Q>mxKcV7XJVn&;U}Gmz@Iu7XJVnf&dtLm(T+M7XJVn@c<aqm)QdVC;tFf_W(-4m)ipX7XJW9>;N6Am*@ik8~*?uyZ{!wm+Aum82<nk`~VyBm+k`qA^!j!@&Fj*m-_<%8UFws&;S_4m<|H~7XJVywE!5Lm>UBCYX1NqqX7t>m?Z-M7XJVroB$Yjm`(!#C;tE#%>X5im|6n>7XJVqdjK16m|+6|8~*?p_5c>`m}>(78~*?n*#IJVn05mI7XJVk)Br-qn0x~O7XJVn$^adxn1KTTCI0|Dxd0Zdn2iGf7XJV<umC4<n3w|qME?L5*#H>Un5P2(7XJVp#Q+<%n7RW182<ns%K#R}n8yPE',2114522125)
install('tda11',800,0,'C;tE_!~h?on9TzK7XJVn(EuLEn9&0O9sd9s+W;27nBoHf7XJVz_5d4&nCSxm8~*?y!2lM)nF0d<7XJVldH@)7nF|8|8~*?@=>QhHnH2*77XJVpwE!NZnHmEC9{&Iq*Z?Q7nK=UhC;tF6(Eu2}nMeZwCI0{xo&X+<nNI@%7XJVp_5c~>nOg$@7XJVkx&RxenP>w57XJVnrT{XcnQQ|97XJVn)c_dGnR5dG7XJVn`v4f#nSBEQ82<nk+W;BDnT!JfA^!jt*Z>%inVkawC;tEz)BrS$nYjZ18~*?n{{U#hncD*Z7XJVn*8musnco8d7XJVnk^nh!nk54O7XJVq&Hx+Enlb|b7XJVpssI_HnmPjj7XJVz_y8Ewno9!!82<nk{{SKInpOh<7XJVnY5-DTnvVkj7XJVlwE!V`nx_K*7XJVy{{S2Dnymu>7XJVnr~nzEnzRD|7XJV;+5j8cn!W=7C;tF9n*cPIn#ltI8~*?nu>c;4n&blj7XJVn)&L&5n(G4q8UFwl^#C39n<xVSCI0{@_W&5|n>zylAO8Rw<p37tn>+&m7XJVp)&LvAn?3^o7XJVn!~h<#n@j@$7XJVn{{S7-n_U9{7XJVn>i`|mn|}iU7XJVlzW^z!n~Vbh82<nk#sDV0n~(zl7XJVpfB+kLo1g;#AO8R+{{R;9o2CN*7XJV*l>i%+o9+VuUH<@@-2m~soB0C(9sd9pzW^JVoE-xI8~*?vjQ}EhoHPRf7XJVn%m5g+oIC>n8~*?n+yEHSoJa!z7XJVkjsP}eoJs=#7XJVn$N(kCoJ|7&8~*?n&Hx#)oKOP*9sd9y>i{C%oLd6`C;tEz-T)(=oL&O}7XJVn?En~ioNfaE7XJVnkN_QqoN@yI82<o%+5jKToP`4b7XJVkyZ|DPoR0$lA^!jv!T?a2oT38&7XJVnkpLNqoUj7`8~*?&-~blboU{V~7XJVkhX5jjoa+Ms7XJVnw*VfNojn5p7XJVkxBw-%oj?Ns7XJVn=>Qn9',895747609)
install('tda12',800,0,'omT?@82<n~zW^PronHe07XJVn=KvU-ooxdE8~*?@&j1#!oqq!W8~*?qvH%#Ooq+=Y7XJVn^Z+7|owEY~9{&IqzW^DZox}qGCI0{zssJ9Uoz(*X7XJVk%m5pMoz?>Y8UFwnzW^Spo#z7p82<nt^8g#go+bkT7XJV;`T!fco+<+X7XJVn(EuH;o-6|Z8~*?p@&Fd{o;d>m7XJVntN<98o<0Kr7XJVxlmHuro=O7%7XJV;{{S2Oo=pP)7XJVq+yEHdo=*b+7XJVny8s=6o@xUCFaH2Nw*Vi7o^1mFGXDS;{{S21o_GTQ7XJVk=>Q?qo_zxV7XJVn$p9#!o`M4a7XJVxlmH)%o{<9pA^!jw*8n2Vo|FRs7XJVzy#N@!o}mK(8~*?n{{SA@o}vQ)7XJVlvj7{Ro}&W*7XJVrtN<>2o}>c+7XJVx;Q$`dp2h<J7XJVryZ|w|p2-6M7XJVpvH&KNpBDoF7XJVv$N(F^pBw`K7XJVn-vAl2pCSVQ82<ns>;N0apFINrFaH1*&;TCLpHBk-7XJWUlK^OWpI-w2CI0{@=l~eupJ4+47XJVq>Hr(epLYWQC;tE##sD6ipMwJc7XJVq(EuCGpV$Kc8UFwq@&FdspXmbt8~*?pga96MpacT|7XJVk_5c~mpa=s18~*?p#Q+wqpc(@J7XJVqy#O1epd<qTHva%aoB%YHpg;ovAO8R-_W&63pict;CI0{(_W&D(pkf067XJVr%m5gspl<^JGXDS;y8s@9po9Ye7XJVk-~b!lppXLq9sd9s&j1#(ppydt9{&Iq<NzD9priu;7XJVq`2ZN%pu+<I82<nv+W;H3pwa^X7XJVqq5vC<p$7v17XJVk{{S@Op&0`J82<n~#sDa|p+N%xFaH21&j2Nzp-=+=CI0{z_W%~(p<@F89{&Iv*#IB3p=bjD8~*?n@&F>tp=tvF8~*?phyWjVp>G2K7XJVn_y8WBp>hKN7XJVnssJCKp@jng7XJVn{{R`qp_Bsv8UFwn',1064830316)
install('tda13',800,0,'_W%~}p_~H%7XJVnumBm0p``-=7XJVk(EuB&p{)Y|8~*?n#sDX=q9g+V7XJV_&;V$%qE`a|7XJV;^8g#@qG|&G7XJVq?*Jd)qK^Xr7XJVn;Q$`hqO1b|8~*?n$^aO|qOSu08~*?n&Hx?GqOk)2JO2O{g91r*qT2%iCI0{$!~jc^qeBA#7XJWM&j2FFqf`R`C;tE+>HsL*qsIdPH~#=0wg4xnqss#TJpTY2@&G5^qy_^37XJVn=>Qn2q!j}I@&5o_^Z=T}q(lP%8UFwl;s6`Eq(}n*7XJVr!vGt+q*Vg|8~*?uxBwQhq-FyE7XJV~&HyLHq;~@V7XJVq<p3Miq=o|kBL4s<=>Q(yq=*9m7XJVpxd2tHr2PW`7XJVn#Q+|pr4s`H82<nn-vArmrGEneDE|N$_y898rIrH#C;tF6{{R;MrKtk|7XJVp-vAibrMv?G82<np=>QhbrOg8X8UFwq=>Qn%rU3&07XJVl`2Zc(rbGh(8~*?p<Ny}dre*^G7XJVn`2Zr~rfLHK7XJVn)&L!?ri23k8~*?z=KvY!rmO=1A^!jtw*VWjrriSo7XJVn<^Up}r!E5k7XJV;@&Fs{r!fNn7XJVkzW^DZr!)fq8~*_y{{R{1r+fnd7XJV&R{$ngr>z437XJVyumBsJr^y2V7XJVnnE)7Ur|km(8~*?~<^X8Jr|<&+DE|N$zW^Sns7nI?7XJVncK{e>s8a&~8~*?n^8gsps96I582<nn^8gm;sGS1<7XJVnegGqCsZav|8~*?p_y88RscQoO7XJV!kpLTVseA(f82<n$-T)cbsfz;u82<np;s77wsf_~w82<nk?*J&nsh$G>7XJV!ZvY=qsigw|QvU!Q!2lMysqq5<9sd9s>i`(msq+H>8~*?n>Hr<ostp4G8~*?p)BqpUs&fMX8~*?ql>j)2s(k|h8UFwl!vG<zs;&b77XJV<VE`Lgs=EUK7XJVk#Q+<vs?q}h7XJVqo&YF*s@DSm8~*?v$N(Rts_p{-',2340688148)
store_list("tds7",[MODEL_ID])
print("Part 7 of 8 installed. Run tinydata8 next.")
