# CalcGPT 3 model installer 6 of 8. Run in order.
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

if installed(6):
 print("Part 6 of 8 already installed; skipping.")
 raise SystemExit
install('tdvc1',800,0,'Z*FXP0B&hxWdM0^btiIV0ApcpCv*U4X#jI?ZDn+5X>Ml#b76S^a&K>K0B~||Vr*q?0Bm7%bO38<Ze##&c4cw^Vqs%z0CjT!Ze@6M0BUby0C#0_WdLn;b94Y~YyfC!Z2)FzZe;*tZ*6d4Zg~K0WnpdrcW7?_cW7y2XaHhmbaZ8M0CZ?&b7cT#X>McyZDDz0WdL(;b#7#H0Ay)oZYOjAc4Yu=VQpmqY-x0KY-Ip!Z+2w>Vs&`{Wq4zCb7cTwY;$h_V`yb#YXEd|c>rN-cVT&R0AgikZ*pY-aAA1>Y-MyOa{zK>0AXfyWpV&>bZKmC0B>|?WpV&yZ)t940BK}pVE}JtW&mhua{z8-c4cw^ZEtR6c>ry1b94Z7Z*6aKa&LD4V_|G;0A^)nYye_qV_|i3WdLk%Z)<68X8?3)VQv6qZ+C70VRLH$b#r9^cV%U30AgWe0B>tyc>rZ>b7cTwW^!R^WB_z%a%E)zVPkZ4VQg%90C0750A^)(0CZ?+ZfA1<ZE0>~0B&h#XmkK$VR8U*b!l{E0AgixbO2~?ZDjyqXJKh>0CZ??b!TXF0BB`la%2E#WqAN*Z*OD(WMO%80C{C$asYE-X=DIxWo2{#Xm4<30CQt#Z*Ob>Xk}q?0Av7fa%5$40A+4xY-w|70BB)yWB_S%ZYOjAXLV(Ba{z5&WMu$jVRB>uVs&!>Z){`$Zgp*9WpV&_Z*psCZf5{xc4cyTbZBXAX8>VlbY*gGZ*Oh@X>N3H0B>eyX=7yoVrgdpY;SLCa{y>>b#r9^d1Ya8a{ys-Z*^{D0ApoxbYW?3Y<U24Xm57_V`yn^WpiZ!Wp-t9c>r*7Wps3T0CZ?&a%CrT0CaC|X=iA30AgiqX=Qe00CjV9VQg%90AXx$WnpA_0Bvb=a{y>zaBz75Yh`6{0C{C}0C#e4Zf5{=Xm4|60C!<&bO2;;Y;0k2a{yv>b7^j6b8`T6XlZU|0A^`+WdLDrZ**v7asXvvbO2*)VRLf;XJvGBX>Ml#aB^v5',137172276)
install('tdvc2',800,0,'WdLJnVQyz-0Ay)yZe?-+ZEtRLXaHzoc4clSbO2*-ZE0?20Bvb*b#!HO0CQn&WdL+&WodE%Y-M3~WdLkpbY%c?WnpA_0CRL<a&!Q5bz^7%VsdG2X8>exZe;*>Z*p>Z0C#V90A+S%asY5_VR-;>Y+++%0Bvb!XmkK)Y++;od2e+mY-|8-Z**vBZf5{<bYXb_Xk{mJ0Az1vb8aVe0A+S%ZUAs$a&&nBVr5}<bZKUFYyfj*Wo>f+cV#DRYyfRxa(Mt{Zf|vGXaHhqbO2*-ZE$sTWpV&604xAM03iT60C#0<V{dI`0CaM7WdLPiV`u<#Z*Oh@a%F90ZDM6|0Ay)qW@U0^Zgc>7bzyD*cW7yBWdLPib9n%FZ*C`a0CjU^WB_zwY-<2-W^`q405LECY-x670B~q;Ze;*>WhZiF0CjF;WpZ<LVQypqXkm6~Zf5{<bZ>9~X>N37a%FRLX>Ml#bZ=~A0C#0>bO2;&WNrXta%paB0AY7wc>rc%asX^$bY*e?b7)~~YyfO!W^@2$Zfb9N0Bvt=Wo~o;VPj)&b#8P3b8l^BZ*FA(b8uy0YXEd;WqBuZWdLP(VPkY`c>ri>XJ`OoZ**t?W?^k<Y<U1-XL4m_0A_M&Wo~410Ap!%c>r^0WhZk0ZDnP2X>Ml#b7gL10B~|;W@T~!X>N37a%FRLWn=(vW@cq_0Bvt}X=MO(XlZV1X>Ml#bairW0B>+*ZUAX*aBp&SVQzE)V_|Y-0CZ?_Z*^yA0B~||Vqs!zc>rc|Wn}<jZ*OY=b8uy2X<=*tV{c|=Wn}<mcyMKIb7^*E0C{C|bY*g6VR-;^WpZ|DV`TtnVQ_F|Ze?TucVTp6XaIC&ZUAO)b#ef6Z*66CX>Db50C{h9a&u*DW&kn(Wp-t5X>Ml#ZDDQzW@&6}0Apxja%W`#ZFzHLY-Rv$b#rNB0CZ_%Yh`o*Vs&$Q0BvD(bY*e?H2`#PXJvF~WpV&!b#4H2Wo2#vXm507Yyfj@VQg#waA9(E0BCP@a&rJ?',1258034687)
install('tdvc3',800,0,'Y-wj`bO2#&ZEtgQ0CQ<>V`TtiXlZU?0CHtvWB_bwW@P|jXKw&=X=iQ#VsCY4XmkK%Z)0?CasX&$a%CrT0A+S%a(QoVWdLGnY-|8`X>(`*GXQXGVQv6oVQy;xaA9&~Zgg`1d2e+mc4Yu#Z*^{Ta(MuEWnpw^WpV&wd1U}*a%p95WB_4oa%pF1bO32?W^ZzBVRUJ4ZUA&)Vr*pqVPb4$0CQz_WpZI`0AginZf5{va%E&`bO2^=a%})}Wpn^@Wn*t{WB_k&V`TtgaA9(EZDnqB0CjG3X>0&D0Ap`+bO3i@bY*e?b#7^PWpZ<Aba?<{VRL8zcVTR60CQ=2WdLJuY-9j*VQgz@Zf5{xcyMKMX=QF>WdLJgb7cT>VRUF^asX&=bO3j6Ze(S0W_4@;V_|G;X>Ml#b8TsKXaH?#Zgq5J0CHt>bYXRJVQzE)aAk64Wn**zcV%U3Wo~2uXm53L0ApcnY-MBsaA{*}0C!<-bY)}!cWGv20Agu!bZBH@c>rN<d3RxX0CRM5Wo2{#GcW*jVQXn_X8>()Z2)v~X>b5@WnpvxY+-U|WdJq+YHw(60C#04c4Yu?Z*ysMX>V=-cW-iRWB_b$b94Z0VQXb`0CQz>X>WCN0B~$&VRLnIWdLSxa%W|90BB)sW&m_{0CQn?0A^u!Z*pmLWdLwxa%f?2a{y#vbY%cB0CZ_>Wpe;`Z*Bl)Z*^{D0BmJpa&7=~X?Or;a%p5?c>p^AZ+C70cV%U3a{yv*Z)<Y^bZ>0{b97;HbY)}!V{C79Xk~K%b76UN0BvDzVP|D>0AY4vX>4I)Y-Ip#VRCY5Wn=(hX>tH$WpH6~bZupBbO10gFaTm@X=-V1X8>()c4Yu%VRCGF0CZ??b!TV*XK8Y50BvDpVQm0(Z*OY=WMyz~b7^z{b8uyDWB_AfZDjy(Z*y~LVr*pqa%E%ycW7yJWdL__X>?@(b8uy0YiVw00CaL;X>I^ya%pyD0Cs6}X><T?Wp{G`Xm4y}0BLS?WpZw1bO3E(',149297104)
install('tdvc4',611,0,'YiVw00Ap`$Wpe;|Z*?bR0CHt>WpZ|5bZKvH0CQ+>a&!Q6a(QWPX8?0$c4ck=VsCSE0CjF;WpV&=Wo~o;b76FKa%5q70BmV)WdL(&bO2>|V`Xe?Wo~o;W_4_A0CaL`Wn=(yb#4G~VQ^(~0A*=(Xk~H$Xklq`0AX@vZYOjAV{dP40AXTtZ)|mRWo&r>XJKt+0CHtvYyfk0ZEa<80A+4u0C#0!asYE^Z*XvFZf5{8FaT$Dc>r{1X>xRV0CZ>ob98lNc>r={V{dJ3Wo~2uaA9(50B<K_Y;R+00AX-&a%E#_VRU5xb9HcVZ*yg20CRP4aBp*E0AX-&Z)t9HZDnqB0AqD@0B~h;b8l_{X>)D>bY*gKX<}?;0Bvt>bZBz`cW-rUWNs&P0CZ(xV`yb^0CaM1bz*E~0A^)nY-w(10BmJpb94Z6Wo2yubY)=xVr*e!YXD<tX>4S2Wo`g-X>Mn1WdLJnZ*OyD0Ap`;aBO7&aB^>AY-Me80Ap`#Z*l-+VQyn(0C#V4Yh`2rWNBt*X=8P4bO32?bY*gOX=Qf+V{dG1WoKmoXkm0^0Ayig0AyujX=G(&0AXkVV`yn(Yh`W#X>@Y{cW7^HWdLw*aCK~9asXj$Z*FG*Y-w|JWo`gvcx7^9X>(-&W@&C|b7*B`0BmJ+bY*e?F*N{pZ*F8|asY5_VR>n8X8>qnZe##$Z**v7asX>-WMpY>X8>$<ZewTwWMyG&0C!<?ZYOjAXmxX9VQypqba!QLba?=DX>w&`0BLS>b#h^DV`TsU',1765202077)
install('tda0',800,0,'01*QK7XJVz#Q+$$01^WL7XJVn*#H>G022cM7XJVnzyKJN02BiN7XJVn;{X`b02KoO7XJVn$^aOr02TuP7XJVnbpRM*02c!Q7XJVnpa2+%02l)R82<nk(f}v302u=S7XJVk)BqmC02%`T8~*?n{s0)m02>1U7XJVn?*JH<02~7V7XJVn<p3Df038DW7XJVq$^aXz03HJX9{&Iq_5d5;03QPY7XJVr+yEHb03ZVZ7XJVk>i{0x03ibaCI0{x`2ZfG03rhb7XJVu-2flj03!nc7XJVnt^gRQ03-td8~*?n>;M?n03`ze7XJVt{{R@#044(f7XJVnoB$Yu04D<g7XJVk+W;BR04M_h7XJV!)c_c{04W0i7XJVrmH-}q04f6j7XJVn*#H=_04oCk7XJVn&Hxyl04xIl7XJVn%K#Xk04)Om7XJVn;{X_%04@Un7XJVn*#H=(051ao82<nk{Qw#505Agp7XJVn>i`(g05Jmq8~*?n{{S7x05SsrGXDS;`~Vxk05bys7XJVlhyWXe05k&t7XJVkwg4Ng05t;u7XJVn)&MoG05$^v7XJVn$N(6t05<~w7XJVn(f~KZ05}5x7XJVk&;U5c067By7XJV_@c<jI06GHz7XJVny#OAo06PN!7XJVn;s6+}06YT#7XJVk^8g#(06hZ$7XJVn-2ff706qf%7XJVk(EuT+06zl&7XJVlxd0oo06+r(7XJVnqW~Um06_x)7XJVnod6h{073%*7XJVn%m5g+07C-+7XJVn$^ag%07L@-7XJW5+W;HV07U};7XJVniU1ga07e4<7XJVns{k0Q07nA=8~*?n^#B>I07wG>7XJVnz5p1f07(M?8~*?q{s0#G07?S@KK}p~yZ~Ff080Y^7XJVnq5vM6089e_7XJVn&HysU08Ik`7XJVkq5vD308Rq{8~*^T>Hrqm08aw|82<nr{Qw*K08j$}7XJVqwE!Eg08s+~8~*?n$p9F;08#@07XJVqmH;J#08;}17XJWK',1205062140)
install('tda1',800,0,'^8g#*08|427XJVky#O1!096A37XJVnvj7;X09FG47XJVr%m5gY09OM57XJVnqyQO=09XS682<nk^#B|109gY78~*?n`2ZRA09pe87XJVk)Bqc{09yk97XJVk)BqdB09*qA7XJVq!~h$@09^wB7XJVky#O1u0A2$C7XJVq#Q+<u0AB+D7XJVn^Z-@H0AK?E7XJVn<Nz4Q0AT|F7XJVn*8m^M0Ad3G7XJVn#sC<%0Am9H8~*?n&j1+10AvFI7XJVn-T)rI0A&LJC;tE_(EuOC0A>RK7XJVn{{SBL0A~XL8~*?n`v4fS0B8dM7XJZF=Kvw*0BHjN8~*?@;Q$uA0BQpO7XJVk>Hr(t0BZvPjsE}}y8srf0Bi#Q7XJVn{Qx240Br*R7XJVn-2fQK0B!>S7XJVn#sC<U0B-{TC;tE#wg4W60B{2U7XJVklK>lm0C58V7XJWB;Q$-P0CEEW7XJVnp#T_>0CNKX9{&Iqpa3j<0CWQYC;tE_qyQy`0CfWZC;tE#=KxCN0Coca7XJVkumB#L0CxibGyec3tN<RR0C)oc7XJVny8s`90C@ud9{&Iq>i`?)0D1!e7XJVnumBj60DA)f7XJVn$p9yq0DJ=g7XJVn@c<d)0DS`h7XJVknE)b`0Dc1i82<nk{Qw*E0Dl7j7XJVn_5c{t0DuDk7XJVn<p3D00D%Jl7XJVk<^UPn0D=Pm7XJVn)c`Wl0D}Vn7XJVnyZ{}P0E7bo7XJVpnE)u40EGhp82<nn+W;NO0EPnq7XJVp!T=k<0EYtr8~*@@w*Vfe0EhzsH2(l6+5i~30Eq(t8~*@_#sC(&0Ez<u7XJVn)&L#S0E+_v7XJVzk^mlQ0E`0w7XJVkvjI)90F46xjsE}}r2rOp0FDCyH~#<__5dF70FMIz7XJV(>Hr^^0FVO!C;tGDrvN6R0FeU#7XJVnj{q2f0Fna$C;tE#_5dEk0Fwg%7XJVntN<8u0F(m&l>Y!Y@c<aO0F?s(7XJVl^Z*^n0G0y)',3110526849)
install('tda2',800,0,'8~*?n^Z*$20G9&*7XJVn+yEJ|0GI;+7XJVn<^UMA0GR^-7XJVnx&RoO0Ga~;7XJWUx&SDP0Gk5<FaH1*_y8r;0GtB=7XJVnhyWsp0G$H>C;tE+`v9Hv0G<N?7XJVp@BkRo0G|T@7XJVn)c_x)0H6Z^p#K0Cu>c;Y0HFf_7XJVkoB$=70HOl`7XJVnmjD=y0HXr{DE|N$-2fiY0Hgx|7XJVn#{eFH0Hp%}8~*?n<^UMY0Hy-~7XJVq^#B{`0H*^08~*?n>;O5a0H^~17XJVr`~V*O0I3527XJVn`~V){0ICB37XJVnvj8Wa0ILH48~*?@$N(0@0IUN5tp5NT)BqNk0IdT67XJVt_W&E-0ImZ79{&KY_5c>`0Ivf88~*?n{{SbX0I&l97XJVntpFvS0I>rA7XJVq<N!$E0I~xB7XJVn!vGkN0J8%C82<nt?Eo9h0JH-D7XJVn)c_dH0JQ@E7XJVn`~Vox0JZ}F7XJVkp8y_$0Jj4G7XJVnvH%#B0JsAH7XJV;?*JRq0J#GICI0}q>;M*#0J;MJ7XJVn_5dE60J{SK8~*?n^#B>R0K5YL7XJVl$p9U@0KEeMC;tEzpa3Fq0KNkN8~*?nzyKMq0KWqO82<nk=>Qwy0KfwP7XJVn#{e0o0Ko$Q7XJVn^#B;d0Kx+R7XJVnvH%#e0K)?S7XJVk?Eu5m0K@|TTmJwU<p37g0L23UGXDS;(f}L20LB9V7XJVn_5c{!0LKFW7XJVn`v4f%0LTLX82<nk;s6`l0LcRYFaH1^+yEK80LlXZ7XJVk!T=t-0Luda8~*?n^#B;J0L%jb7XJVn*#OMW0L=pc7XJVnq5vOr0L}vd7XJVn^#C880M7#e8UFwq{{R-*0MG*f7XJVr#{e6+0MP>g8UFy$`T!#30MY{h7XJVk{{S1y0Mi2i7XJVn^8gvO0Mr8j9{&Is>;N6$0M!Ek7XJVq{{S2F0M-Kl7XJVnw*Vu90M`Qm9sd9u>Hr_$0N4Wn7XJVn%m5h4',917239702)
install('tda3',800,0,'0NDco7XJVnw*VcQ0NMip7XJVk!~h$e0NVoq7XJVnssJIO0NeurH2(k_jsO;p0Nn!s7XJVn<p3DV0Nw)t7XJVn;{YM!0N(=u8~*?n_5dBj0N?`v8~*?n`v4j30O11w7XJVn=l~d^0OA7x8~*?u=>Qqi0OJDy7XJV?)&N780OSJz7XJVpq5vD70ObP!<^KQ{`v4oP0OkV#7XJVl>Hr?u0Otb$7XJVqxBwrp0O$h%7XJVk!vG$+0O<n&7XJVk<^Unt0O|t(7XJVny8sxN0P6z)8~*?n(*P&10PF(*7XJVpngAP;0PO<+?f(E4iU1pm0PX_-82<nk`v4o#0Ph0;82<np=KvPa0Pq6<7XJVn?f@O20PzC=@&5o_zW|z|0P+I>7XJV_`T%Id0P_O?^Zx)D=l~Y10Q3U@7XJVniU2fx0QCa^7XJVn^8hl|0QLg_82<n$vj8WN0QUm`_x}JM$^aRk0Qds{7XJVlt^gaR0Qmy|7XJVz-2gL;0Qv&}8~*?n)&Ll-0Q&;~7XJVkuK*i|0Q>_0KK}sx+W;260R001{r><Kwg6X^0R9627XJVt(*Pc~0RIC3|Nj6M!2oEO0RRI48UFwn^#B&@0RaO57XJVrxd0oT0RjU6C;tE+;Q<1^0Rsa78~*?n_5c~k0R#g8C;tE&^Z*v)0R;m97XJVnsQ?|80R{sA7XJVzSpXkX0S5yB7XJVndjKbN0SE&C8UFwt=>Qnl0SN;D8~*?n{{R^O0SW^E7XJVn@BkyI0Sf~F7XJVn)Brxp0Sp5H4F3QY`T!op0SyBH7XJVn{{S7@0S*HI7XJVl=Kvkl0S^NJ7XJVn-~bto0T2TK9sd9p@c<al0TBZL8~*?n&Hx?60TKfM8~*?q+yEBM0TTlN7XJVn`T!V~0TcrO7XJVz@Bkz50TlxP8~*?n{{R^30Tu%Q7XJWfp8y-50T%-R7XJVk#Q-$L0T=@S7XJVxi~tyj0T}}T8UFwl_y8O00U84U7XJVnfB+wN0UHAV7XJVn',863824628)
install('tda4',800,0,')BqT&0UQGW82<ns&Hx#+0UZMX7XJVn^Z*^o0UiSY82<nk{{SEH0UrYZ8~*?n$pAEp0U!ebApZax%>Ws(0U-kcA^!j!+5j8M0U`qc8~*?n@c<a=0V4weBmV#vqW~L&0VD$e82<oh>i`+o0VM+f8~*?wyZ|q?0VV?g8~*?np8y_*0Ve|h7XJVp>Hrwl0Vo3i82<nr(*PF50Vx9j7XJVku>c>N0V)Fk7XJVn)&Ll&0V@Ll7XJVn-vAhv0W1Rm8~*?n@c<>p0WAXn7XJVk{{S2C0WJdo82<n#;Q$u60WSjp7XJVqqW~S00Wbpq7XJVq#sD3Y0Wkvr7XJY;%>Wq90Wt#s7XJVnp#VdW0W$*t8~*?n=Kv$b0W<>u7XJV)kN_on0W|{v7XJVn>HsId0X72xHva$?<^UPy0XG8x8~*?n{{SBG0XPEy8~*?p^8gmw0XYKzA^!j$>HuBF0XhQ!X#W5f_yBCh0XqW#7XJVl{{R@~0Xzc$7XJVn=l~hu0X+i%tp5NVq5#Z~0X_o&7XJVl=KvVU0Y3u(7XJVp$N(F{0YC!)7XJVn?Eyff0YL)*7XJVqhX5af0YU=+82<np;Q$uS0Yd`-82<nk-T)iU0Yn1;7XJVqzW^AQ0Yw7<82<nk?f@R$0Y(D=7XJVkyZ|1s0Y?J>7XJVp?Eo0g0Zjt{X#W5u{{SD|0Zsz|8~*?n-vA!W0Z#(}8~*?p;{YAa0Z;<~8~*?w_5c>h0Z{`07XJVz_y8N?0a6117XJVn*Z>*W0aF727XJV~tpQVz0aOD37XJVn>i`(U0aXJ47XJVlqyQhJ0agP57XJV_lK>-#0apV67XJVn)&MS_0ayb79sd9#(*PFJ0a*h87XJVq@Bt0s0a^n98~*?n-vA%i0b2tA9{&I(wE<hN0bBzCT>k(e&;S<60bK(C8~*?q^#B&@0bT<D7XJVn;{X}d0bc_E82<np@BkLu0bm0F7XJVn#{eUz0bv6G7XJVpxd0oo0b&CH7XJVn_5c~?0b>II',3723482622)
store_list("tds6",[MODEL_ID])
print("Part 6 of 8 installed. Run tinydata7 next.")
