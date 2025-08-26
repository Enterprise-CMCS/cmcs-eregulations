<script setup>
import { inject } from "vue";
import { useRoute } from "vue-router";

import AccessLink from "@/components/AccessLink.vue";
import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import SignInLink from "@/components/SignInLink.vue";
import JumpTo from "@/components/JumpTo.vue";
import HeaderUserWidget from "@/components/header/HeaderUserWidget.vue";

const adminUrl = inject("adminUrl");
const apiUrl = inject("apiUrl");
const customLoginUrl = inject("customLoginUrl");
const homeUrl = inject("homeUrl");
const isAuthenticated = inject("isAuthenticated");
const manualUrl = inject("manualUrl");
const searchUrl = inject("searchUrl");
const statutesUrl = inject("statutesUrl");
const subjectsUrl = inject("subjectsUrl");
const obbbaUrl = inject("obbbaUrl");
const username = inject("username");

const $route = useRoute();
</script>

<template>
    <div class="ds-base obbba-page">
        <header id="header" class="sticky">
            <HeaderComponent :home-url="homeUrl">
                <template #jump-to>
                    <JumpTo :api-url="apiUrl" :home-url="homeUrl" />
                </template>
                <template #links>
                    <HeaderLinks
                        :manual-url="manualUrl"
                        :statutes-url="statutesUrl"
                        :subjects-url="subjectsUrl"
                        :obbba-url="obbbaUrl"
                    />
                </template>
                <template #search>
                    <HeaderSearch :search-url="searchUrl" />
                </template>
                <template v-if="isAuthenticated" #sign-in>
                    <HeaderUserWidget :admin-url="adminUrl">
                        <template #username>
                            {{ username }}
                        </template>
                    </HeaderUserWidget>
                </template>
                <template v-else #sign-in>
                    <SignInLink
                        :custom-login-url="customLoginUrl"
                        :home-url="homeUrl"
                        :is-authenticated="isAuthenticated"
                        :route="$route"
                    />
                </template>
                <template #get-access>
                    <AccessLink v-if="!isAuthenticated" :base="homeUrl" />
                </template>
            </HeaderComponent>
        </header>
        <div id="obbbaApp" class="site-container">
            <div class="obbba__container">
                <h1>One Big Beautiful Bill Act (OBBBA)</h1>

                <p>
                    Excerpt from <a
                        href="https://www.congress.gov/bill/119th-congress/house-bill/1/text"
                        class="external"
                        target="_blank"
                    >H.R.1 — One Big Beautiful Bill Act</a> (Public Law No. 119-21, July 4, 2025), Title VII — Finance, Subtitle B — Health.
                </p>
                <p>
                    Additions to the Social Security Act are <span class="annotated-text">highlighted with a background color</span>.
                </p>

                <!--<div class="lbexTocSubTitleOLC">
                    <a href="#toc-H00A124B5E74D481E9C40B11626C9DADE" id="H00A124B5E74D481E9C40B11626C9DADE">Subtitle B—Health</a>
                </div>-->
                <div class="lbexTocDivisionOLC">
                    <a id="H1F2AC7DAAC144B50AAB0E9E039D9BE3C" href="#toc-H1F2AC7DAAC144B50AAB0E9E039D9BE3C">Chapter 1 — Medicaid</a>
                </div>
                <div class="lbexTocSubChapterOLC">
                    <a id="H92BA8B5040914BF4B6F9A50225F8E976" href="#toc-H92BA8B5040914BF4B6F9A50225F8E976">Subchapter A — Reducing fraud and improving enrollment processes</a>
                </div>
                <span class="lbexTocSectionOLC">
                    <a id="H8DEEC3F1F40E4CD390DAC8E9F3F90B6C" href="#toc-H8DEEC3F1F40E4CD390DAC8E9F3F90B6C">Sec. 71101. Moratorium on implementation of rule relating to eligibility and enrollment in Medicare Savings Programs.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="H6CCF8B8A04E04A36847FD683A259E8DC" href="#toc-H6CCF8B8A04E04A36847FD683A259E8DC">Sec. 71102. Moratorium on implementation of rule relating to eligibility and enrollment for Medicaid, CHIP, and the Basic Health Program.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="HA52179FF1EA542DA88936E2159BEFC99" href="#toc-HA52179FF1EA542DA88936E2159BEFC99">Sec. 71103. Reducing duplicate enrollment under the Medicaid and CHIP programs.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="H968D7B63B96D4B7F849C3F7D820864FE" href="#toc-H968D7B63B96D4B7F849C3F7D820864FE">Sec. 71104. Ensuring deceased individuals do not remain enrolled.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="HCA190EE79A494B7B807E4370E04565D6" href="#toc-HCA190EE79A494B7B807E4370E04565D6">Sec. 71105. Ensuring deceased providers do not remain enrolled.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="HE4C5D821764A4ED89B23CB28D9795390" href="#toc-HE4C5D821764A4ED89B23CB28D9795390">Sec. 71106. Payment reduction related to certain erroneous excess payments under Medicaid.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="H606041EC9E7F4E47BF27FA785F990CD4" href="#toc-H606041EC9E7F4E47BF27FA785F990CD4">Sec. 71107. Eligibility redeterminations.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="HAC580CB2660842A98524C26BC39A0B5D" href="#toc-HAC580CB2660842A98524C26BC39A0B5D">Sec. 71108. Revising home equity limit for determining eligibility for long-term care services under the Medicaid program.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="H81AF8E812F034407AFF9A4E9B8533848" href="#toc-H81AF8E812F034407AFF9A4E9B8533848">Sec. 71109. Alien Medicaid eligibility.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="H01B260BD1A734C8384AF364D82D3132E" href="#toc-H01B260BD1A734C8384AF364D82D3132E">Sec. 71110. Expansion FMAP for emergency Medicaid.</a>
                </span>
                <div class="lbexTocSubChapterOLC">
                    <a id="H7D8B025C07364BD8B6BD2B6E5C3D1861" href="#toc-H7D8B025C07364BD8B6BD2B6E5C3D1861">Subchapter B — Preventing wasteful spending</a>
                </div>
                <span class="lbexTocSectionOLC">
                    <a id="H72D966A2232743E5A94F076C68AE84D0" href="#toc-H72D966A2232743E5A94F076C68AE84D0">Sec. 71111. Moratorium on implementation of rule relating to staffing standards for long-term care facilities under the Medicare and Medicaid programs.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="H917F6C03CA464B319B70F26A163C0EE0" href="#toc-H917F6C03CA464B319B70F26A163C0EE0">Sec. 71112. Reducing State Medicaid costs.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="H4C4222AD5DC6485391D3BF42FAE4785C" href="#toc-H4C4222AD5DC6485391D3BF42FAE4785C">Sec. 71113. Federal payments to prohibited entities.</a>
                </span>
                <div class="lbexTocSubChapterOLC">
                    <a id="H33AAEB14AE494C8981C870486D3E3901" href="#toc-H33AAEB14AE494C8981C870486D3E3901">Subchapter C — Stopping abusive financing practices</a>
                </div>
                <span class="lbexTocSectionOLC">
                    <a id="H027BCCE030064EC1801736510E3BFF79" href="#toc-H027BCCE030064EC1801736510E3BFF79">Sec. 71114. Sunsetting increased FMAP incentive.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="HC5CF4567712D420786321990FC6F05A3" href="#toc-HC5CF4567712D420786321990FC6F05A3">Sec. 71115. Provider taxes.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="H5095A31A390141E1AF3A2DAD32DD6532" href="#toc-H5095A31A390141E1AF3A2DAD32DD6532">Sec. 71116. State directed payments.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="HFC9712978086448A884AD4DA6242CFF0" href="#toc-HFC9712978086448A884AD4DA6242CFF0">Sec. 71117. Requirements regarding waiver of uniform tax requirement for Medicaid provider tax.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="H3DFC92C358834F5B82DE8AB81465692A" href="#toc-H3DFC92C358834F5B82DE8AB81465692A">Sec. 71118. Requiring budget neutrality for Medicaid demonstration projects under section 1115.</a>
                </span>
                <div class="lbexTocSubChapterOLC">
                    <a id="H41B4BE6053784F329BB924FD89F29721" href="#toc-H41B4BE6053784F329BB924FD89F29721">Subchapter D — Increasing personal accountability</a>
                </div>
                <span class="lbexTocSectionOLC">
                    <a id="HE10C293F1AD14FEE88FED90835BFBB2D" href="#toc-HE10C293F1AD14FEE88FED90835BFBB2D">Sec. 71119. Requirement for States to establish Medicaid community engagement requirements for certain individuals.</a>
                </span>
                <span class="lbexTocSectionOLC">
                    <a id="H4ADCA385302C45CCBDC2C4550A5A6759" href="#toc-H4ADCA385302C45CCBDC2C4550A5A6759">Sec. 71120. Modifying cost sharing requirements for certain expansion individuals under the Medicaid program.</a>
                </span>
                <div class="lbexTocSubChapterOLC">
                    <a id="H2388F94754554D3C9E54A32152DEE520" href="#toc-H2388F94754554D3C9E54A32152DEE520">Subchapter E — Expanding Access to Care</a>
                </div>
                <span class="lbexTocSectionOLC">
                    <a id="H09652BCC85234E4FAAAC9D9A805494AF" href="#toc-H09652BCC85234E4FAAAC9D9A805494AF">Sec. 71121. Making certain adjustments to coverage of home or community-based services under Medicaid.</a>
                </span>

                <!--<div>
                    <a href="#H00A124B5E74D481E9C40B11626C9DADE" id="toc-H00A124B5E74D481E9C40B11626C9DADE">
                    <span class="lbexSubTitleLevelOLC">Subtitle B — Health</span>
                    </a>
                </div>-->
                <div>
                    <a id="toc-H1F2AC7DAAC144B50AAB0E9E039D9BE3C" href="#H1F2AC7DAAC144B50AAB0E9E039D9BE3C">
                        <span class="lbexChapterLevelOLC">Chapter 1 — Medicaid</span>
                    </a>
                </div>
                <div>
                    <a id="toc-H92BA8B5040914BF4B6F9A50225F8E976" href="#H92BA8B5040914BF4B6F9A50225F8E976">
                        <span class="lbexSubChapterLevelOLC">Subchapter A — Reducing fraud and improving enrollment processes</span>
                    </a>
                </div>

                <span class="lbexHang">
                    <a id="toc-H8DEEC3F1F40E4CD390DAC8E9F3F90B6C" href="#H8DEEC3F1F40E4CD390DAC8E9F3F90B6C">
                        <span id="H8DEEC3F1F40E4CD390DAC8E9F3F90B6C" class="lbexHangWithMargin">
                            <span class="lbexSectionlevelOLC">Sec. 71101. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Moratorium on implementation of rule relating to eligibility and enrollment in Medicare Savings Programs</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="HDCE6E7E5FDA94A8285704957AF3AC72B" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">In general</span>.—The Secretary of Health and Human Services shall not, during the period beginning on the date of the enactment of this section and ending September 30, 2034, implement, administer, or enforce the amendments made by the provisions of the final rule published by the Centers for Medicare &amp; Medicaid Services on September 21, 2023, and titled “Streamlining Medicaid; Medicare Savings Program Eligibility Determination and Enrollment” (<a
                        href="https://www.federalregister.gov/documents/2023/09/21/2023-20382/streamlining-medicaid-medicare-savings-program-eligibility-determination-and-enrollment"
                        class="external"
                        target="_blank"
                    >88 Fed. Reg. 65230</a>) to the following sections of title 42, Code of Federal Regulations:
                    <a id="HB1281369669C4648A3250EE470A075F2" />
                    <span class="lbexIndentParagraph">(1) Section <a
                        href="https://www.ecfr.gov/current/title-42/part-406/section-406.21#p-406.21(c)"
                        class="external"
                        target="_blank"
                    >406.21(c)</a>.</span>
                    <a id="HCE8D6997B5854B01ADD71E9E21FDC2BA" />
                    <span class="lbexIndentParagraph">(2) Section <a href="/42/435/Subpart-A/#435-4">435.4</a>.</span>
                    <a id="H15487E3B744248DCAFBFE927D8DA0D58" />
                    <span class="lbexIndentParagraph">(3) Section <a href="/42/435/Subpart-G/#435-601">435.601</a>.</span>
                    <a id="HE50E09359ADF43E3801583A7F93536AF" />
                    <span class="lbexIndentParagraph">(4) Section <a href="/42/435/Subpart-J/#435-911">435.911</a>.</span>
                    <a id="H0118D4FC9FB141779DBAFFFC5D16CE70" />
                    <span class="lbexIndentParagraph">(5) Section <a href="/42/435/Subpart-J/#435-952">435.952</a>.</span>
                </span>
                <a id="H598825FE57D945BF99919E631E2EB252" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">Implementation funding</span>.—For the purposes of carrying out the provisions of this section and section 71102, there are appropriated, out of any monies in the Treasury not otherwise appropriated, to the Administrator of the Centers for Medicare &amp; Medicaid Services, $1,000,000 for fiscal year 2026, to remain available until expended.
                </span>

                <span class="lbexHang">
                    <a id="toc-H6CCF8B8A04E04A36847FD683A259E8DC" href="#H6CCF8B8A04E04A36847FD683A259E8DC">
                        <span id="H6CCF8B8A04E04A36847FD683A259E8DC" class="lbexHangWithMargin">
                            <span class="lbexSectionlevelOLC">Sec. 71102. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Moratorium on implementation of rule relating to eligibility and enrollment for Medicaid, CHIP, and the Basic Health Program</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <span class="lbexIndent">
                    <span class="lbexIndentSectionText">The Secretary of Health and Human Services shall not, during the period beginning on the date of the enactment of this section and ending September 30, 2034, implement, administer, or enforce the amendments made by the provisions of the final rule published by the Centers for Medicare &amp; Medicaid Services on April 2, 2024, and titled “Medicaid Program; Streamlining the Medicaid, Children's Health Insurance Program, and Basic Health Program Application, Eligibility Determination, Enrollment, and Renewal Processes” (<a
                        href="https://www.federalregister.gov/documents/2024/04/02/2024-06566/medicaid-program-streamlining-the-medicaid-childrens-health-insurance-program-and-basic-health"
                        class="external"
                        target="_blank"
                    >89 Fed. Reg. 22780</a>) to the following sections of title 42, Code of Federal Regulations:
                    </span>
                </span>
                <a id="H7D21A4884F4A482E92B6D806BB64376D" />
                <span class="lbexIndentParagraph">(1) PART 431.—
                    <a id="H077E344340DA4CC1B6AE74AE55D63DA8" />
                    <span class="lbexIndentSubpar">(A) Section <a href="/42/431/Subpart-E/#431-213-d">431.213(d)</a>.</span>
                </span>


                <a id="H42237E815BFE4C90A3BA673ED5A0ED07" />
                <span class="lbexIndentParagraph">(2) PART 435.—
                    <a id="H71F74C30E9514D2087EC3E585BF8CE25" />
                    <span class="lbexIndentSubpar">(A) Section <a href="/42/435/Subpart-C/#435-222">435.222</a>.</span>

                    <a id="H832B46669A6A4A16B4FB89126EFD832D" />
                    <span class="lbexIndentSubpar">(B) Section <a href="/42/435/Subpart-E/#435-407">435.407</a>.</span>

                    <a id="H97F1770CA51C4362A7342F5BC96622F4" />
                    <span class="lbexIndentSubpar">(C) Section <a href="/42/435/Subpart-J/#435-907">435.907</a>.</span>

                    <a id="HDBE4C453DE744C719C74B723C40666E9" />
                    <span class="lbexIndentSubpar">(D) Section <a href="/42/435/Subpart-J/#435-911-c">435.911(c)</a>.</span>

                    <a id="H36BD5BABE098435794D3D3767A35C301" />
                    <span class="lbexIndentSubpar">(E) Section <a href="/42/435/Subpart-J/#435-912">435.912</a>.</span>

                    <a id="H227480A09C3449659DC628114682795B" />
                    <span class="lbexIndentSubpar">(F) Section <a href="/42/435/Subpart-J/#435-916">435.916</a>.</span>

                    <a id="H7C655D554F6B411287E964B71B34A247" />
                    <span class="lbexIndentSubpar">(G) Section <a href="/42/435/Subpart-J/#435-919">435.919</a>.</span>

                    <a id="H4B4A827E4C334187A9A1A89EF051394C" />
                    <span class="lbexIndentSubpar">(H) Section <a href="/42/435/Subpart-M/#435-1200-b-3-i">435.1200(b)(3)(i)-(v)</a>.</span>

                    <a id="HECA656E702634947B790993D7C5800B3" />
                    <span class="lbexIndentSubpar">(I) Section <a href="/42/435/Subpart-M/#435-1200-e0a428659af526a4235cd9a2ecbb904a">435.1200(e )(1)(ii)</a>.</span>

                    <a id="H79250E195F0843D2B9137692544CA717" />
                    <span class="lbexIndentSubpar">(J) Section <a href="/42/435/Subpart-M/#435-1200-h-1">435.1200(h)(1)</a>.</span>
                </span>


                <a id="H7352215019274DF88BBA1292F84BB0AC" />
                <span class="lbexIndentParagraph">(3) PART 447.—Section <a href="/42/447/Subpart-A/#447-56-a-1-v">447.56(a)(1)(v)</a>.</span>

                <a id="H79BA1C0B1BC34A219585A104FE35B757" />
                <span class="lbexIndentParagraph">(4) PART 457.—
                    <a id="H218ABEFEACEC48048D19B9725B66DC3F" />
                    <span class="lbexIndentSubpar">(A) Section <a href="/42/457/Subpart-C/#457-344">457.344</a>.</span>

                    <a id="HFFCC5AF3EAD546DB82645A047A623B28" />
                    <span class="lbexIndentSubpar">(B) Section <a
                        href="https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-D/part-457/subpart-I/section-457.960"
                        class="external"
                        target="_blank"
                    >457.960</a>.</span>

                    <a id="H1E0BF50F724843B2BE354F98D8490127" />
                    <span class="lbexIndentSubpar">(C) Section <a href="/42/457/Subpart-K/#457-1140-d-4">457.1140(d)(4)</a>.</span>

                    <a id="H82BF3A5429C2459D8CE8DE8BA7FDC46F" />
                    <span class="lbexIndentSubpar">(D) Section <a href="/42/457/Subpart-K/#457-1170">457.1170</a>.</span>

                    <a id="H59115532E4B94D6AB62D59E8A8D259B3" />
                    <span class="lbexIndentSubpar">(E) Section <a href="/42/457/Subpart-K/#457-1180">457.1180</a>.</span>
                </span>

                <span class="lbexHang">
                    <a id="toc-HA52179FF1EA542DA88936E2159BEFC99" href="#HA52179FF1EA542DA88936E2159BEFC99">
                        <span class="lbexHangWithMargin">
                            <span id="HA52179FF1EA542DA88936E2159BEFC99" />
                            <span class="lbexSectionlevelOLC">Sec. 71103. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Reducing duplicate enrollment under the Medicaid and CHIP programs</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="H1F7ABBF243574F56885FF65CE98A5BB4" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">Medicaid</span>.—
                    <a id="H4FE266775AFB4A558143D02CDF85AD60" />
                    <span class="lbexIndentParagraph">(1) IN GENERAL.—Section 1902 of the Social Security Act (<a
                        href="https://uscode.house.gov/quicksearch/get.plx?title=42&amp;section=1396a"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396a</a>) is amended—
                        <a id="H29D75E6989BC4EFDAA7301B36F3938E0" />
                        <span class="lbexIndentSubpar">(A) in subsection (a)—
                            <a id="H92C72A7C36744FFD90024D4910C8DCEA" />
                            <span class="lbexIndentClause">(i) in paragraph (86), by striking “and” at the end;</span>
                            <a id="H7FC53B2F724B4ED8819238A68648C063" />
                            <span class="lbexIndentClause">(ii) in paragraph (87), by striking the period and inserting <span class="annotated-text">“; and”</span>; and</span>
                            <a id="H4A73910A19DC46759686010826F13E41" />
                            <span class="lbexIndentClause">(iii) by inserting after paragraph (87) the following new paragraph:
                                <!--<span class="lbexIndentClause">-->
                                <a id="HE0BAE9757ADE4768A18598F8286BB37F" />
                                <span class="lbexIndentParagraph annotated-text">“(88) provide—
                                    <a id="HECEF746EAAE942D1A09114F35257EEF1" />
                                    <span class="lbexIndentSubpar">“(A) beginning not later than January 1, 2027, in the case of 1 of the 50 States and the District of Columbia, for a process to regularly obtain address information for individuals enrolled under such plan (or a waiver of such plan) in accordance with subsection (vv); and</span>
                                    <a id="H110A23CCBB284B608C7D5A1C1ED7483A" />
                                    <span class="lbexIndentSubpar">“(B) beginning not later than October 1, 2029—
                                        <a id="H8D634CB2B6D94DB8B17778E70B38490B" />
                                        <span class="lbexIndentClause">“(i) for the State to submit to the system established by the Secretary under subsection (uu), with respect to an individual enrolled or seeking to enroll under such plan, not less frequently than once each month and during each determination or redetermination of the eligibility of such individual for medical assistance under such plan (or waiver of such plan)—
                                            <a id="H990F35F42DB24DB5988C86B9B4C43507" />
                                            <span class="lbexIndentSubclause">“(I) the social security number of such individual, if such individual has a social security number and is required to provide such number to enroll under such plan (or waiver); and</span>
                                            <a id="H0C7AE05534094C259FCAA34CC99F1C7B" />
                                            <span class="lbexIndentSubclause">“(II) such other information with respect to such individual as determined necessary by the Secretary for purposes of preventing individuals from simultaneously being enrolled under State plans (or waivers of such plans) of multiple States;</span>
                                        </span>
                                        <a id="H40F2D01C78E84EA7AE9F0070DBDF6812" />
                                        <span class="lbexIndentClause">“(ii) for the use of such system to prevent such simultaneous enrollment; and</span>
                                        <a id="HC5D6130D28B84780BC0FB8D63AEA5A61" />
                                        <span class="lbexIndentClause">“(iii) in the case that such system indicates that an individual enrolled or seeking to enroll under such plan (or waiver of such plan) is enrolled under a State plan (or waiver of such a plan) of another State, for the taking of appropriate action (as determined by the Secretary) to identify whether such an individual resides in the State and disenroll an individual from the State plan of such State if such individual does not reside in such State (unless such individual meets such an exception as the Secretary may specify).”; and</span>
                                    </span>
                                </span>
                                <!--</span>-->
                            </span>
                        </span>
                        <a id="H7D06E840F81642728077A429B81D4C50" />
                        <span class="lbexIndentSubpar">(B) by adding at the end the following new subsections:
                            <span class="lbexIndentClause">
                                <a id="H4F3055E7B7F54F369F040A997F87A278" />
                                <span class="lbexIndentSubsection">
                                    <span class="lbexIndent">“(uu)
                                        <span class="lbexSectionLevelOLCnuclear">Prevention of enrollment under multiple State plans</span>.—
                                        <a id="H36E78966EB40404B91B8E0341205CFF2" />
                                        <span class="lbexIndentParagraph">“(1) IN GENERAL.—Not later than October 1, 2029, the Secretary shall establish a system to be utilized by the Secretary and States to prevent an individual from being simultaneously enrolled under the State plans (or waivers of such plans) of multiple States. Such system shall—
                                            <a id="H215880F962994AB2B4A5E2D941A40957" />
                                            <span class="lbexIndentSubpar">“(A) provide for the receipt of information submitted by a State under subsection (a)(88)(B)(i); and</span>
                                            <a id="H240A63FCCA3D4A2FBAC1ED935D96708E" />
                                            <span class="lbexIndentSubpar">“(B) not less than once each month, transmit information to a State (or allow the Secretary to transmit information to a State) regarding whether an individual enrolled or seeking to enroll under the State plan of such State (or waiver of such plan) is enrolled under the State plan (or waiver of such plan) of another State.</span>
                                        </span>
                                    </span>
                                    <a id="H7FF47C0405A14E4EBA8BA37D30D14502" />
                                    <span class="lbexIndentParagraph">“(2) STANDARDS.—The Secretary shall establish such standards as determined necessary by the Secretary to limit and protect information submitted under such system and ensure the privacy of such information, consistent with subsection (a)(7).</span>
                                    <a id="H76BFE964C8B343E88A803CB342319C58" />
                                    <span class="lbexIndentParagraph">“(3) IMPLEMENTATION FUNDING.—There are appropriated to the Administrator of the Centers for Medicare &amp; Medicaid Services, out of amounts in the Treasury not otherwise appropriated, in addition to amounts otherwise available—
                                        <a id="H4860126CACBA40D78E198D55A6F6DB19" />
                                        <span class="lbexIndentSubpar">“(A) for fiscal year 2026, $10,000,000 for purposes of establishing the system and standards required under this subsection, to remain available until expended; and</span>
                                        <a id="HE46C6A76F8E045E3A817FBDFFA067F65" />
                                        <span class="lbexIndentSubpar">“(B) for fiscal year 2029, $20,000,000 for purposes of maintaining such system, to remain available until expended.</span>
                                    </span>
                                </span>

                                <a id="H9CF84C72551B43B8B0D1A446C36447CC" />
                                <span class="lbexIndentSubsection">
                                    <span class="lbexIndent">“(vv)
                                        <span class="lbexSectionLevelOLCnuclear">Process to obtain enrollee address information</span>.—
                                        <a id="H6B08E24A8558487DB44CFF6780A11E8A" />
                                        <span class="lbexIndentParagraph">“(1) IN GENERAL.—For purposes of subsection (a)(88)(A), a process to regularly obtain address information for individuals enrolled under a State plan (or a waiver of such plan) shall obtain address information from reliable data sources described in <a href="#HB306F21862C44B0CA7EF4830FE6F617C">paragraph (2)</a> and take such actions as the Secretary shall specify with respect to any changes to such address based on such information.</span>
                                    </span>
                                    <a id="HB306F21862C44B0CA7EF4830FE6F617C" />
                                    <span class="lbexIndentParagraph">“(2) RELIABLE DATA SOURCES DESCRIBED.—For purposes of <a href="#H6B08E24A8558487DB44CFF6780A11E8A">paragraph (1)</a>, the reliable data sources described in this paragraph are the following:
                                        <a id="H11BF6C87222F4EBBAEE325155B8A597D" />
                                        <span class="lbexIndentSubpar">“(A) Mail returned to the State by the United States Postal Service with a forwarding address.</span>
                                        <a id="H11DA7B886BF546B6923A90930D97A2E9" />
                                        <span class="lbexIndentSubpar">“(B) The National Change of Address Database maintained by the United States Postal Service.</span>
                                        <a id="HFC1A5F2745554FB3B56DC1CE6815A65A" />
                                        <span class="lbexIndentSubpar">“(C) A managed care entity (as defined in section 1932(a)(1)(B)) or prepaid inpatient health plan or prepaid ambulatory health plan (as such terms are defined in section 1903(m)(9)(D)) that has a contract under the State plan if the address information is provided to such entity or plan directly from, or verified by such entity or plan directly with, such individual.</span>

                                        <a id="H83A1948F3D354BCFA30602589B2CB58B" />
                                        <span class="lbexIndentSubpar">“(D) Other data sources as identified by the State and approved by the Secretary.”.</span>
                                    </span>
                                </span>
                            </span>
                        </span>
                    </span>
                </span>

                <a id="HF4A376B90ABF4D5F8E0A240F9F2F11F4" />
                <span class="lbexIndentParagraph">(2) CONFORMING AMENDMENTS.—
                    <a id="HB74BBF87B95342CD9D5397956A44F7A8" />
                    <span class="lbexIndentSubpar">(A) PARIS.—Section 1903(r)(3) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396b&num=0&edition=prelim#substructure-location_r_3"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396b(r)(3)</a>) is amended—
                        <a id="HAED89D0C277C406DB490421E38C54FF9" />
                        <span class="lbexIndentClause">(i) by striking “In order” and inserting <a id="HAAEAC589BF8A461784A7ADC6C7EAF86E" /><span class="annotated-text">“(A) In order”</span>;</span>
                        <a id="HD80B61629C4348B98D2E52F0EC48BE1E" />
                        <span class="lbexIndentClause">(ii) by striking “through the Public” and inserting <span class="annotated-text">“through—</span>
                            <a id="H588E9E03B31C4B6DB3180012729864A1" />
                            <span class="lbexIndentSubpar"><span class="annotated-text">“(i) the Public”</span>;</span>
                        </span>

                        <a id="HD2B282B4E612493F800D88CD7B7C3FEE" />
                        <span class="lbexIndentClause">(iii) by striking the period at the end and inserting  <span class="annotated-text">“; and</span><a id="H1E443FA2F30F47C9A0F52C682AA33025" />
                            <span class="lbexIndentSubpar"><span class="annotated-text">“(ii) beginning October 1, 2029, the system established by the Secretary under section 1902(uu).”</span>; and</span>
                        </span>

                        <a id="H500874F55953484ABF8A11D6A03581A7" />
                        <span class="lbexIndentClause">(iv) by adding at the end the following new subparagraph:
                            <!--<span class="lbexIndentClause">-->
                            <a id="HE17D24771B7140D9B1654596AF62C547" />
                            <span class="lbexIndentParagraph annotated-text">“(B) Beginning October 1, 2029, the Secretary may determine that a State is not required to have in operation an eligibility determination system which provides for data matching (for purposes of address verification under section 1902(vv)) through the system described in subparagraph (A)(i) to meet the requirements of this paragraph.”.</span>
                            <!--</span>-->
                        </span>
                    </span>

                    <a id="H29669828A6FE4AA8807F272ECC1881B0" />
                    <span class="lbexIndentSubpar">(B) MANAGED CARE.—Section 1932 of the Social Security Act (<a
                        href="https://uscode.house.gov/quicksearch/get.plx?title=42&amp;section=1396u-2"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396u–2</a>) is amended by adding at the end the following new subsection:
                        <span class="lbexIndentClause">
                            <a id="H485D9261171A42E39982056C679E22E9" />
                            <span class="lbexIndentSubsection">
                                <span class="lbexIndent">“(j)
                                    <span class="lbexSectionLevelOLCnuclear">Transmission of address information</span>.—Beginning January 1, 2027, each contract under a State plan with a managed care entity (as defined in section 1932(a)(1)(B)) or with a prepaid inpatient health plan or prepaid ambulatory health plan (as such terms are defined in section 1903(m)(9)(D)), shall provide that such entity or plan shall promptly transmit to the State any address information for an individual enrolled with such entity or plan that is provided to such entity or plan directly from, or verified by such entity or plan directly with, such individual.”.</span>
                            </span>
                        </span>
                    </span>
                </span>

                <a id="H9065F8FB95A143EDAFE49C6B9A488D23" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">CHIP</span>.—
                    <a id="H5459CCDF4E1540A7A72D53384E8236A5" />
                    <span class="lbexIndentParagraph">(1) IN GENERAL.—Section 2107(e)(1) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1397gg&num=0&edition=prelim#substructure-location_e_1"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1397gg(e)(1)</a>) is amended—
                        <a id="H01E621F5CF5549EC9B37D6336CB88616" />
                        <span class="lbexIndentSubpar">(A) by redesignating subparagraphs (H) through (U) as subparagraphs (I) through (V), respectively; and</span>
                        <a id="H7601260C757B4E5CAFECB144B27B5582" />
                        <span class="lbexIndentSubpar">(B) by inserting after subparagraph (G) the following new subparagraph:
                            <span class="lbexIndentClause">
                                <a id="H484C499F3943455387EFDE07A6E1AFBE" />
                                <span class="lbexIndentSubpar annotated-text">“(H) Section 1902(a)(88) (relating to address information for enrollees and prevention of simultaneous enrollments).”.</span>
                            </span>
                        </span>
                    </span>

                    <a id="HC4AD55EEC3074DA5B1BFA04CB250B1DE" />
                    <span class="lbexIndentParagraph">(2) MANAGED CARE.—Section 2103(f)(3) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1397cc&num=0&edition=prelim#substructure-location_f_3"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1397cc(f)(3)</a>) is amended by striking “and (e)” and inserting <span class="annotated-text">“(e), and (j)”</span>. </span>
                </span>

                <span class="lbexHang">
                    <a id="toc-H968D7B63B96D4B7F849C3F7D820864FE" href="#H968D7B63B96D4B7F849C3F7D820864FE">
                        <span class="lbexHangWithMargin">
                            <span id="H968D7B63B96D4B7F849C3F7D820864FE" />
                            <span class="lbexSectionlevelOLC">Sec. 71104. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Ensuring deceased individuals do not remain enrolled</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <span class="lbexIndent">
                    <span class="lbexIndent">Section 1902 of the Social Security Act (<a
                        href="https://uscode.house.gov/quicksearch/get.plx?title=42&amp;section=1396a"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396a</a>), as amended by section 71103, is further amended—</span>
                </span>
                <a id="H3CEA26DD1A90412181B5EB0CAD6C7A1D" />
                <span class="lbexIndentParagraph">(1) in subsection (a)—
                    <a id="H93674B5332954A50A00A82CD77AEB615" />
                    <span class="lbexIndentSubpar">(A) in paragraph (87), by striking “; and” and inserting a semicolon;</span>
                    <a id="H75BEA9ADD42D45948A889F540489655A" />
                    <span class="lbexIndentSubpar">(B) in paragraph (88), by striking the period at the end and inserting <span class="annotated-text">“; and”</span>; and</span>

                    <a id="H28034D8913A949C491BD8972010E4D20" />
                    <span class="lbexIndentSubpar">(C) by inserting after paragraph (88) the following new paragraph:
                        <span class="lbexIndent">
                            <a id="HFEC8260E2A8941AA8BED96F1CD37E6E0" />
                            <span class="lbexIndentParagraph"><span class="annotated-text">“(89) provide that the State shall comply with the eligibility verification requirements under subsection (ww), except that this paragraph shall apply only in the case of the 50 States and the District of Columbia.”</span>; and</span>
                        </span>
                    </span>
                </span>
                <a id="H0114D7B732AD4747A8D68538D3674EF8" />
                <span class="lbexIndentParagraph">
                    <span class="lbexIndent">(2) by adding at the end the following new subsection:
                        <a id="HE532F0E04DBB40249C17F3F4A0E4E5E8" />
                        <span class="lbexIndentSubsection">
                            <span class="lbexIndent">“(ww)
                                <span class="lbexSectionLevelOLCnuclear">Verification of certain eligibility criteria</span>.—
                                <a id="HCD5D4B3BB14947E4A0E13D32B9CA7AE1" />
                                <span class="lbexIndentParagraph">“(1) IN GENERAL.—For purposes of subsection (a)(89), the eligibility verification requirements, beginning January 1, 2027, are as follows:
                                    <a id="H5C2B87985FC448F9926F2AE296802A3F" />
                                    <span class="lbexIndentSubpar">“(A) QUARTERLY SCREENING TO VERIFY ENROLLEE STATUS.—The State shall, not less frequently than quarterly, review the Death Master File (as such term is defined in section 203(d) of the Bipartisan Budget Act of 2013) or a successor system that provides such information needed to determine whether any individuals enrolled for medical assistance under the State plan (or waiver of such plan) are deceased.</span>
                                    <a id="HB209D730BDD9449A8241021814B58A99" />
                                    <span class="lbexIndentSubpar">“(B) DISENROLLMENT UNDER STATE PLAN.—If the State determines, based on information obtained from the Death Master File, that an individual enrolled for medical assistance under the State plan (or waiver of such plan) is deceased, the State shall—
                                        <a id="H401463914CD047AC844756679456EB9B" />
                                        <span class="lbexIndentClause">“(i) treat such information as factual information confirming the death of a beneficiary;</span>
                                        <a id="H7D2BD2003F654F549613B646348B21E9" />
                                        <span class="lbexIndentClause">“(ii) disenroll such individual from the State plan (or waiver of such plan) in accordance with subsection (a)(3); and</span>
                                        <a id="H8E359A35940449659C2BD39E718D1EB7" />
                                        <span class="lbexIndentClause">“(iii) discontinue any payments for medical assistance under this title made on behalf of such individual (other than payments for any items or services furnished to such individual prior to the death of such individual).</span>
                                    </span>
                                    <a id="H91FB921D901A42C5B89BE16269CF42A5" />
                                    <span class="lbexIndentSubpar">“(C) REINSTATEMENT OF COVERAGE IN THE EVENT OF ERROR.—If a State determines that an individual was misidentified as deceased based on information obtained from the Death Master File and was erroneously disenrolled from medical assistance under the State plan (or waiver of such plan) based on such misidentification, the State shall immediately re-enroll such individual under the State plan (or waiver of such plan), retroactive to the date of such disenrollment.</span>

                                    <a id="H713FB5BB431841E7A14C7FBB59FD30E8" />
                                    <span class="lbexIndentParagraph">“(2) RULE OF CONSTRUCTION.—Nothing under this subsection shall be construed to preclude the ability of a State to use other electronic data sources to timely identify potentially deceased beneficiaries, so long as the State is also in compliance with the requirements of this subsection (and all other requirements under this title relating to Medicaid eligibility determination and redetermination).”.</span>
                                </span>
                            </span>
                        </span>
                    </span>
                </span>

                <span class="lbexIndentParagraph" />

                <span class="lbexHang">
                    <a id="toc-HCA190EE79A494B7B807E4370E04565D6" href="#HCA190EE79A494B7B807E4370E04565D6">
                        <span class="lbexHangWithMargin">
                            <span id="HCA190EE79A494B7B807E4370E04565D6" />
                            <span class="lbexSectionlevelOLC">Sec. 71105. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Ensuring deceased providers do not remain enrolled</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <span class="lbexIndent">
                    <span class="lbexIndentSectionText">Section 1902(kk)(1) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396a&num=0&edition=prelim#substructure-location_kk_1"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396a(kk)(1)</a>) is amended—</span>
                </span>
                <a id="H44B9AB1660C54E77A865E21461DA9417" />
                <span class="lbexIndentParagraph">(1) by striking “The State” and inserting:
                    <span class="ul">
                        <a id="H48181FB255E34F0CBFCA4DF07AC56942" />
                        <span class="lbexIndentSubpar"><span class="annotated-text">“(A) IN GENERAL.—The State”</span>; and</span>
                    </span>
                </span>

                <a id="H146F9AE098B841E0819A164C5BD087F7" />
                <span class="lbexIndentParagraph">(2) by adding at the end the following new subparagraph:
                    <span class="ul">
                        <a id="HEA870FE36510417E9035410B46DF758A" />
                        <span class="lbexIndentSubpar annotated-text">“(B) PROVIDER SCREENING AGAINST DEATH MASTER FILE.—Beginning January 1, 2028, as part of the enrollment (or reenrollment or revalidation of enrollment) of a provider or supplier under this title, and not less frequently than quarterly during the period that such provider or supplier is so enrolled, the State conducts a check of the Death Master File (as such term is defined in section 203(d) of the Bipartisan Budget Act of 2013) to determine whether such provider or supplier is deceased.”.</span>
                    </span>
                </span>

                <span class="lbexHang">
                    <a id="toc-HE4C5D821764A4ED89B23CB28D9795390" href="#HE4C5D821764A4ED89B23CB28D9795390">
                        <span class="lbexHangWithMargin">
                            <span id="HE4C5D821764A4ED89B23CB28D9795390" />
                            <span class="lbexSectionlevelOLC">Sec. 71106. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Payment reduction related to certain erroneous excess payments under Medicaid</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="HC670A843FC9F4238A6146494C352067E" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">In general</span>.—Section 1903(u)(1) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396b&num=0&edition=prelim#substructure-location_u_1"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396b(u)(1)</a>) is amended—
                    <a id="H937661ADD6DD4AEF85F4B0D80F0F6BE5" />
                    <span class="lbexIndentParagraph">(1) in subparagraph (A)—
                        <a id="H320636DB2653442A8D4CB2402575EC9B" />
                        <span class="lbexIndentSubpar">(A) by inserting <span class="annotated-text">“for audits conducted by the Secretary, or, at the option of the Secretary, audits conducted by the State”</span> after “exceeds 0.03”; and</span>
                        <a id="H1327C1E313D64E5E9483CAF10A9AEA2D" />
                        <span class="lbexIndentSubpar">(B) by inserting <span class="annotated-text">“, to the extent practicable”</span> before the period at the end;</span>
                    </span>
                </span>

                <a id="H9F4052C1574343A9B5EBBB963994AB01" />
                <span class="lbexIndentParagraph">(2) in subparagraph (B)—
                    <a id="H62624980F5B14CEBB6CBC24C04F18AFB" />
                    <span class="lbexIndentSubpar">(A) by striking “The Secretary” and inserting  <a id="H1EEF7073D128493D95B7DD59A52715B4" /><span class="annotated-text">“(i) Subject to clause (ii), the Secretary”</span>; and</span>
                    <a id="H578C033173624FFD9BD6E547177B4571" />
                    <span class="lbexIndentSubpar">(B) by adding at the end the following new clause:
                        <span class="lbexIndentClause">
                            <a id="HDEE2DAC6C3174262A3D30C3A5339A462" />
                            <span class="lbexIndentParagraph annotated-text">“(ii) The amount waived under clause (i) for a fiscal year may not exceed an amount equal to the erroneous excess payments for medical assistance described in subparagraph (D)(i)(II) made for such fiscal year that exceed the allowable error rate of 0.03.”.</span>
                        </span>
                    </span>
                </span>

                <a id="H4CB87149B0144BD8A00E1A8F686C830E" />
                <span class="lbexIndentParagraph">(3) in subparagraph (C), by striking “he” in each place it appears and inserting <span class="annotated-text">“the Secretary”</span> in each such place; and</span>

                <a id="HB5D63D3AFA4D4FB197D36B748A75AB6C" />
                <span class="lbexIndentParagraph">(4) in subparagraph (D)(i)—
                    <a id="H800494C02307471D9555A99DCB201917" />
                    <span class="lbexIndentSubpar">(A) in subclause (I), by striking “and” at the end;</span>
                    <a id="HDE92A8E3B7A44D3B8A813585DD3727ED" />
                    <span class="lbexIndentSubpar">(B) in subclause (II), by striking the period at the end and inserting <span class="annotated-text">“, or payments where insufficient information is available to confirm eligibility, and”</span>; and</span>
                    <a id="H737E592431FF4C5B9BB4A352F478DDAC" />
                    <span class="lbexIndentSubpar">(C) by adding at the end the following new subclause:
                        <span class="lbexIndentClause">
                            <a id="H95A5F06B71B44967A102B4D9BC1B7D00" />
                            <span class="lbexIndentParagraph annotated-text">“(III) payments (other than payments described in subclause (I)) for items and services furnished to an individual who is not eligible for medical assistance under the State plan (or a waiver of such plan) with respect to such items and services, or payments where insufficient information is available to confirm eligibility.”.</span>
                        </span>
                    </span>
                </span>

                <a id="H28D27A71AA1745A1A09AB0CF48607EDA" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">Effective date</span>.—The amendments made by subsection (a) shall apply beginning with respect to fiscal year 2030.</span>

                <span class="lbexHang">
                    <a id="toc-H606041EC9E7F4E47BF27FA785F990CD4" href="#H606041EC9E7F4E47BF27FA785F990CD4">
                        <span class="lbexHangWithMargin">
                            <span id="H606041EC9E7F4E47BF27FA785F990CD4" />
                            <span class="lbexSectionlevelOLC">Sec. 71107. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Eligibility redeterminations</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="H17BE0BEBA4774BD2AC044EDEDBDC0FDC" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">In general</span>.—Section 1902(e)(14) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396a&num=0&edition=prelim#substructure-location_e_14"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396a(e)(14)</a>) is amended by adding at the end the following new subparagraph:
                    <span class="lbexIndent">
                        <a id="H2EB8DD9335D24D5A8B16BADFE2D61E52" />
                        <span class="lbexIndentSubpar annotated-text">“(L) FREQUENCY OF ELIGIBILITY REDETERMINATIONS FOR CERTAIN INDIVIDUALS.—
                            <a id="HFD6637C0F5224E02BEA2FA7F5DD88570" />
                            <span class="lbexIndentClause">“(i) IN GENERAL.—Subject to clause (ii), with respect to redeterminations of eligibility for medical assistance under a State plan (or waiver of such plan) scheduled on or after the first day of the first quarter that begins after December 31, 2026, a State shall make such a redetermination once every 6 months for the following individuals:
                                <a id="H674E7D3A9DCE478593D331F9FE24910F" />
                                <span class="lbexIndentSubclause">“(I) Individuals enrolled under subsection (a)(10)(A)(i)(VIII).</span>
                                <a id="H44422F1978A4463FA00A5337D5FDFC64" />
                                <span class="lbexIndentSubclause">“(II) Individuals described in such subsection who are otherwise enrolled under a waiver of such plan that provides coverage that is equivalent to minimum essential coverage (as described in <a
                                    href="https://uscode.house.gov/quicksearch/get.plx?title=26&amp;section=5000A"
                                    class="external"
                                    target="_blank"
                                >section 5000A(f)(1)(A)</a> of the Internal Revenue Code of 1986 and determined in accordance with standards prescribed by the Secretary in regulations) to all individuals described in subsection (a)(10)(A)(i)(VIII).</span>
                            </span>
                            <a id="HCAE581DC60574A9390E4B2970B78EFE2" />
                            <span class="lbexIndentClause">“(ii) EXEMPTION.—The requirements described in clause (i) shall not apply to any individual described in subsection (xx)(9)(A)(ii)(II).</span>

                            <a id="H5B3F9FB19302417AB1FC202CFE641FDE" />
                            <span class="lbexIndentClause">“(iii) STATE DEFINED.—For purposes of this subparagraph, the term ‘State’ means 1 of the 50 States or the District of Columbia.”.</span>
                        </span>
                    </span>
                </span>

                <a id="H2FF54D1ABEFF4EE59EEA17996BA035C8" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">Guidance</span>.—Not later than 180 days after the date of enactment of this section, the Secretary of Health and Human Services, acting through the Administrator of the Centers for Medicare &amp; Medicaid Services, shall issue guidance relating to the implementation of the amendments made by this section.</span>
                <a id="H0B26574C8AED4B1D88572CE1657E0315" />
                <span class="lbexIndent">(c)
                    <span class="lbexSectionLevelOLCnuclear">Implementation funding</span>.—For the purposes of carrying out the provisions of, and the amendments made by, this section, there are appropriated, out of any monies in the Treasury not otherwise appropriated, to the Administrator of the Centers for Medicare &amp; Medicaid Services, $75,000,000 for fiscal year 2026, to remain available until expended.</span>

                <span class="lbexHang">
                    <a id="toc-HAC580CB2660842A98524C26BC39A0B5D" href="#HAC580CB2660842A98524C26BC39A0B5D">
                        <span class="lbexHangWithMargin">
                            <span id="HAC580CB2660842A98524C26BC39A0B5D" />
                            <span class="lbexSectionlevelOLC">Sec. 71108. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Revising home equity limit for determining eligibility for long-term care services under the Medicaid program</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="HAFFB5AB97A84416A8CA2844C876D3889" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">Revising home equity limit</span>.—Section 1917(f)(1) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396p&num=0&edition=prelim#substructure-location_f_1"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396p(f)(1)</a>) is amended—
                    <a id="H1D7250775A944D8293EE8C07BD26B67F" />
                    <span class="lbexIndentParagraph">(1) in subparagraph (B)—
                        <a id="H10606F5F8B2A4A0380B43FF39F2FEBFC" />
                        <span class="lbexIndentSubpar">(A) by striking “A State” and inserting <span class="annotated-text">“(i) A State”</span>; </span>
                        <a id="H2D59538C96B344D798CB483F10AA8B90" />
                        <span class="lbexIndentSubpar">(B) in clause (i), as inserted by subparagraph (A)—
                            <a id="H1FC72A4476F24CAE94008B86F751AA96" />
                            <span class="lbexIndentClause">(i) by striking “<span class="lbexThinSpace" />‘$500,000’” and inserting <span class="annotated-text">“the amount specified in subparagraph (A)”</span>; and </span>
                            <a id="H736A7B4BB6084DF99AE37BE1EEF5EABD" />
                            <span class="lbexIndentClause">(ii) by inserting <span class="annotated-text">“, in the case of an individual’s home that is located on a lot that is zoned for agricultural use,”</span> after “apply subparagraph (A)”; and</span>
                        </span>
                        <a id="H84EB889031B9425B8BF2A1A546D345B9" />
                        <span class="lbexIndentSubpar">(C) by adding at the end the following new clause:
                            <span class="lbexIndentClause">
                                <a id="HB6BBF12010B443E984E90B1AB752D144" />
                                <span class="lbexIndentParagraph"><span class="annotated-text">“(ii) A State may elect, without regard to the requirements of section 1902(a)(1) (relating to statewideness) and section 1902(a)(10)(B) (relating to comparability), to apply subparagraph (A), in the case of an individual’s home that is not described in clause (i), by substituting for the amount specified in such subparagraph, an amount that exceeds such amount, but does not exceed $1,000,000.”</span>; and</span>
                            </span>
                        </span>
                    </span>
                </span>
                <a id="HB1364FFE24A24CC699667E9B4508C967" />
                <span class="lbexIndentParagraph">(2) in subparagraph (C)—
                    <a id="HB9A2F5F5F71644AA84BC594D38552C1B" />
                    <span class="lbexIndentSubpar">(A) by inserting <span class="annotated-text">“(other than the amount specified in subparagraph (B)(ii) (relating to certain non-agricultural homes))”</span> after “specified in this paragraph”; and</span>
                    <a id="HE94B0F476E964210B1C6430F17B358FF" />
                    <span class="lbexIndentSubpar">(B) by adding at the end the following new sentence: <span class="annotated-text">“In the case that application of the preceding sentence would result in a dollar amount (other than the amount specified in subparagraph (B)(i) (relating to certain agricultural homes)) exceeding $1,000,000, such amount shall be deemed to be equal to $1,000,000.”</span>.</span>
                </span>
                <a id="HE9B43645948347829A70DCF2C7126573" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">Clarification</span>.—Section 1902 of the Social Security Act (<a
                        href="https://uscode.house.gov/quicksearch/get.plx?title=42&amp;section=1396a"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396a</a>) is amended—
                    <a id="H80D48AF8E729464185445F88D15F6E82" />
                    <span class="lbexIndentParagraph">(1) in subsection (r)(2), by adding at the end the following new subparagraph:
                        <span class="lbexIndentSubsection">
                            <a id="H855DFEE9E5FF483C8E67D0292122ECEB" />
                            <span class="lbexIndentParagraph">“(C) This paragraph shall not be construed as permitting a State to determine the eligibility of an individual for medical assistance with respect to nursing facility services or other long-term care services without application of the limit under section 1917(f)(1).”; and</span>
                        </span>
                    </span>
                </span>
                <a id="H0A4A6572B23B4E77A87C1B87FDD3E562" />
                <span class="lbexIndentParagraph">(2) in subsection (e)(14)(D)(iv)—
                    <a id="HBA4C203D7AA34B76AE24E32E6592A288" />
                    <span class="lbexIndentSubpar">(A) by striking “Subparagraphs” and inserting
                        <span class="lbexIndentClause">
                            <a id="HA551CE75AEEC49DD93BC4AE73BD8541A" />
                            <span class="lbexIndentSubclause"><span class="annotated-text">“(I) IN GENERAL.—Subparagraphs”</span>; and</span>
                        </span>
                    </span>
                    <a id="HF12A37CF3E194A06A0627BAC9E51CDFB" />
                    <span class="lbexIndentSubpar">(B) by adding at the end the following new subclause:
                        <span class="lbexIndentClause">
                            <a id="H3DDDE3E0FEFE477BBF6CE1F27012D7E5" />
                            <span class="lbexIndentSubclause annotated-text">“(II) APPLICATION OF HOME EQUITY INTEREST LIMIT.—Section 1917(f) shall apply for purposes of determining the eligibility of an individual for medical assistance with respect to nursing facility services or other long-term care services.”.</span>
                        </span>
                    </span>
                </span>

                <a id="HF16E39B9F98E4C67A1EBF92977E7BFE3" />
                <span class="lbexIndent">(c)
                    <span class="lbexSectionLevelOLCnuclear">Effective date</span>.—The amendments made by subsection (a) shall apply beginning on January 1, 2028.</span>

                <span class="lbexHang">
                    <a id="toc-H81AF8E812F034407AFF9A4E9B8533848" href="#H81AF8E812F034407AFF9A4E9B8533848">
                        <span class="lbexHangWithMargin">
                            <span id="H81AF8E812F034407AFF9A4E9B8533848" />
                            <span class="lbexSectionlevelOLC">Sec. 71109. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Alien Medicaid eligibility</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="HCEC62AA2268345DEB0305C1D76EE56A5" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">Medicaid</span>.—Section 1903(v) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396b&num=0&edition=prelim#substructure-location_v"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396b(v)</a>) is amended—
                    <a id="HD4FE61EC0B304D7F858FCB05CBCA0AF1" />
                    <span class="lbexIndentParagraph">(1) in paragraph (1), by striking “and (4)”and inserting <span class="annotated-text">“, (4), and (5)”</span>; and</span>
                </span>
                <a id="H81367C78DE704553ACB9308C562F84D6" />
                <span class="lbexIndentParagraph">(2) by adding at the end the following new paragraph:
                    <span class="lbexIndentSubsection">
                        <a id="HD6D86B4AE5DF48A096908297692DE61A" />
                        <span class="lbexIndentParagraph">“(5) Notwithstanding the preceding paragraphs of this subsection, beginning on October 1, 2026, except as provided in paragraphs (2) and (4), in no event shall payment be made to a State under this section for medical assistance furnished to an individual unless such individual is—
                            <a id="HD8E5CEEE69824BD1ABF6C935870F92A6" />
                            <span class="lbexIndentParagraph">“(A) a resident of 1 of the 50 States, the District of Columbia, or a territory of the United States; and</span>
                            <a id="H4A93BA9E34214DD2A7D28DB2FB531FFB" />
                            <span class="lbexIndentParagraph">“(B) either—
                                <a id="HB65EC1BFA89A4F8D814CC40E101188B9" />
                                <span class="lbexIndentSubpar">“(i) a citizen or national of the United States;</span>
                                <a id="H481189C32FBA49369E4D4C6C88471497" />
                                <span class="lbexIndentSubpar">“(ii) an alien lawfully admitted for permanent residence as an immigrant as defined by sections 101(a)(15) and 101(a)(20) of the Immigration and Nationality Act, excluding, among others, alien visitors, tourists, diplomats, and students who enter the United States temporarily with no intention of abandoning their residence in a foreign country;</span>
                                <a id="HFD723DC1E31B4F2CB929BED23707A23C" />
                                <span class="lbexIndentSubpar">“(iii) an alien who has been granted the status of Cuban and Haitian entrant, as defined in section 501(e) of the Refugee Education Assistance Act of 1980 (Public Law 96–422); or</span>
                                <a id="H93A65B7F5B164649BA9518C81EFD7879" />
                                <span class="lbexIndentSubpar">“(iv) an individual who lawfully resides in the United States in accordance with a Compact of Free Association referred to in section 402(b)(2)(G) of the Personal Responsibility and Work Opportunity Reconciliation Act of 1996.”.</span>
                            </span>
                        </span>
                    </span>
                </span>

                <a id="HC1F149850909487AA2B1B770D794CB52" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">CHIP</span>.—Section 2107(e)(1) of the Social Security Act, as amended by section 71103(b), is further amended—
                    <a id="H6DCEE0AE60DB461E997B867DBC45FABB" />
                    <span class="lbexIndentParagraph">(1) by redesignating subparagraphs (R) through (V) as paragraphs (S) through (W), respectively; and</span>
                </span>
                <a id="H9B0C5982AB4444BA94DB2233C8A92B57" />
                <span class="lbexIndentParagraph">(2) by inserting after paragraph (Q) the following:
                    <span class="lbexIndentSubsection">
                        <a id="H7B00BC264C8F486EB8AF653C885F5AB9" />
                        <span class="lbexIndentSubpar">“(R) Section 1903(v)(5) (relating to payments for medical assistance furnished to aliens), except in relation to payments for services provided under section 2105(a)(1)(D)(ii).”.</span>
                    </span>
                </span>

                <a id="H8F0DFF8D8CA946A4B01365159AE6AAAD" />
                <span class="lbexIndent">(c)
                    <span class="lbexSectionLevelOLCnuclear">Implementation funding</span>.—For the purposes of carrying out the provisions of, and the amendments made by, this section, there are appropriated, out of any monies in the Treasury not otherwise appropriated, to the Administrator of the Centers for Medicare &amp; Medicaid Services, $15,000,000 for fiscal year 2026, to remain available until expended.</span>

                <span class="lbexHang">
                    <a id="toc-H01B260BD1A734C8384AF364D82D3132E" href="#H01B260BD1A734C8384AF364D82D3132E">
                        <span class="lbexHangWithMargin">
                            <span id="H01B260BD1A734C8384AF364D82D3132E" />
                            <span class="lbexSectionlevelOLC">Sec. 71110. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Expansion FMAP for emergency Medicaid</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="H050F12666B2B40318BF49AFC9987802E" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">In general</span>.—Section 1905 of the Social Security Act (<a
                        href="https://uscode.house.gov/quicksearch/get.plx?title=42&amp;section=1396d"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396d</a>) is amended by adding at the end the following new subsection:
                    <span class="lbexIndent">
                        <a id="H9FB7AB9C8BC74E728D697815C49908A6" />
                        <span class="lbexIndentSubsection">
                            <span class="lbexIndentParagraph">“(kk)
                                <span class="lbexSectionLevelOLCnuclear">FMAP for treatment of an emergency Medical condition</span>.—Notwithstanding subsection (y) and (z), beginning on October 1, 2026, the Federal medical assistance percentage for payments for care and services described in paragraph (2) of subsection 1903(v) furnished to an alien described in paragraph (1) of such subsection shall not exceed the Federal medical assistance percentage determined under subsection (b) for such State.”.</span>
                        </span>
                    </span>
                </span>
                <a id="H1501404A856D4183A4C1D6501ADE191C" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">Implementation funding</span>.—For the purposes of carrying out the provisions of, and the amendments made by this section, there are appropriated, out of any monies in the Treasury not otherwise appropriated, to the Administrator of the Centers for Medicare &amp; Medicaid Services, $1,000,000 for fiscal year 2026, to remain available until expended.</span>
                <span id="H7D8B025C07364BD8B6BD2B6E5C3D1861" />

                <a id="toc-H7D8B025C07364BD8B6BD2B6E5C3D1861" href="#H7D8B025C07364BD8B6BD2B6E5C3D1861">
                    <span class="lbexSubChapterLevelOLC">Subchapter B — Preventing wasteful spending</span>
                </a>

                <span class="lbexHang">
                    <a id="toc-H72D966A2232743E5A94F076C68AE84D0" href="#H72D966A2232743E5A94F076C68AE84D0">
                        <span class="lbexHangWithMargin">
                            <span id="H72D966A2232743E5A94F076C68AE84D0" />
                            <span class="lbexSectionlevelOLC">Sec. 71111. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Moratorium on implementation of rule relating to staffing standards for long-term care facilities under the Medicare and Medicaid programs</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <span class="lbexIndent">
                    <span class="lbexIndentSectionText">The Secretary of Health and Human Services shall not, during the period beginning on the date of the enactment of this section and ending September 30, 2034, implement, administer, or enforce the amendments made by the provisions of the final rule published by the Centers for Medicare &amp; Medicaid Services on May 10, 2024, and titled “Medicare and Medicaid Programs; Minimum Staffing Standards for Long-Term Care Facilities and Medicaid Institutional Payment Transparency Reporting” (<a
                        href="https://www.federalregister.gov/documents/2024/05/10/2024-08273/medicare-and-medicaid-programs-minimum-staffing-standards-for-long-term-care-facilities-and-medicaid"
                        class="external"
                        target="_blank"
                    >89 Fed. Reg. 40876</a>) to the following sections of part 483 of title 42, Code of Federal Regulations:
                    </span>
                </span>
                <a id="H7F27631AC8864ABFA997B72C9BC9AAAE" />
                <span class="lbexIndentParagraph">(1) Section <a href="/42/483/Subpart-B/#483-5">483.5</a>.</span>

                <a id="H0BE34688028F490A991FA0D537331D4C" />
                <span class="lbexIndentParagraph">(2) Section <a href="/42/483/Subpart-B/#483-35">483.35</a>.</span>

                <span class="lbexHang">
                    <a id="toc-H917F6C03CA464B319B70F26A163C0EE0" href="#H917F6C03CA464B319B70F26A163C0EE0">
                        <span class="lbexHangWithMargin">
                            <span id="H917F6C03CA464B319B70F26A163C0EE0" />
                            <span class="lbexSectionlevelOLC">Sec. 71112. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Reducing State Medicaid costs</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="HD7F49CCDD9744A4C9F10E968B0298EB9" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">In general</span>.—Section 1902(a)(34) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396a&num=0&edition=prelim#substructure-location_a_34"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396a(a)(34)</a>) is amended to read as follows:
                    <span class="lbexIndent">
                        <a id="HE18F24CA7F044890943FAC0DA62F8375" />
                        <span class="lbexIndentParagraph annotated-text">“(34) provide that in the case of any individual who has been determined to be eligible for medical assistance under the plan and—
                            <a id="HABF0243D137C4AA8B98F4D8875E2E04A" />
                            <span class="lbexIndentSubpar">“(A) is enrolled under paragraph (10)(A)(i)(VIII), such assistance will be made available to the individual for care and services included under the plan and furnished in or after the month before the month in which the individual made application (or application was made on the individual's behalf in the case of a deceased individual) for such assistance if such individual was (or upon application would have been) eligible for such assistance at the time such care and services were furnished; or</span>
                            <a id="H55BFC9A247D3475FB96FE86F1273D8C6" />
                            <span class="lbexIndentSubpar">“(B) is not described in subparagraph (A), such assistance will be made available to the individual for care and services included under the plan and furnished in or after the second month before the month in which the individual made application (or application was made on the individual's behalf in the case of a deceased individual) for such assistance if such individual was (or upon application would have been) eligible for such assistance at the time such care and services were furnished;”.</span>
                        </span>
                    </span>
                </span>

                <a id="HC7870E6A3EC949A3AB2EA6683E9D3219" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">Definition of medical assistance</span>.—Section 1905(a) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396d&num=0&edition=prelim#substructure-location_a"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396d(a)</a>) is amended by striking “in or after the third month before the month in which the recipient makes application for assistance” and inserting <span class="annotated-text">“, with respect to an individual described in section 1902(a)(34)(A), in or after the month before the month in which the recipient makes application for assistance, and with respect to an individual described in section 1902(a)(34)(B), in or after the second month before the month in which the recipient makes application for assistance”</span>.</span>
                <a id="H961706CDB4CE450EAD37A45CDA1206E3" />
                <span class="lbexIndent">(c)
                    <span class="lbexSectionLevelOLCnuclear">CHIP</span>.—Section 2102(b)(1)(B) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1397bb&num=0&edition=prelim#substructure-location_b_1_B"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1397bb(b)(1)(B)</a>) is amended—
                    <a id="H2AA0CC0458554F91931A26C651EAEB34" />
                    <span class="lbexIndentParagraph">(1) in clause (iv), by striking “and” at the end;</span>
                </span>
                <a id="HD94E93B3A7144BFC848CAF55069DA188" />
                <span class="lbexIndentParagraph">(2) in clause (v), by striking the period and inserting <span class="annotated-text">“; and”</span>; and</span>

                <a id="HF55E911FC4D649C4984C7062780E3B55" />
                <span class="lbexIndentParagraph">(3) by adding at the end the following new clause:
                    <span class="lbexIndentSubsection">
                        <a id="HB10DC290DEAF42A0B0A7F283E1C87241" />
                        <span class="lbexIndentClause">“(vi) shall, in the case that the State elects to provide child health or pregnancy-related assistance to an individual for any period prior to the month in which the individual made application for such assistance (or application was made on behalf of the individual), provide that such assistance is not made available to such individual for items and services included under the State child health plan (or waiver of such plan) that are furnished before the second month preceding the month in which such individual made application (or application was made on behalf of such individual) for assistance.”.</span>
                    </span>
                </span>

                <a id="H307C9CEE4E6045A181249FCFFAF74981" />
                <span class="lbexIndent">(d)
                    <span class="lbexSectionLevelOLCnuclear">Effective date</span>.—The amendments made by this section shall apply to medical assistance, child health assistance, and pregnancy-related assistance with respect to individuals whose eligibility for such medical assistance, child health assistance, or pregnancy-related assistance is based on an application made on or after the first day of the first quarter that begins after December 31, 2026.</span>
                <a id="HD5E6ED4B41D14BFB82D78510111D31D3" />
                <span class="lbexIndent">(e)
                    <span class="lbexSectionLevelOLCnuclear">Implementation funding</span>.—For the purposes of carrying out the provisions of, and the amendments made by, this section, there are appropriated, out of any monies in the Treasury not otherwise appropriated, to the Administrator of the Centers for Medicare &amp; Medicaid Services, $10,000,000 for fiscal year 2026, to remain available until expended.</span>

                <span class="lbexHang">
                    <a id="toc-H4C4222AD5DC6485391D3BF42FAE4785C" href="#H4C4222AD5DC6485391D3BF42FAE4785C">
                        <span class="lbexHangWithMargin">
                            <span id="H4C4222AD5DC6485391D3BF42FAE4785C" />
                            <span class="lbexSectionlevelOLC">Sec. 71113. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Federal payments to prohibited entities</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="HDEFFE6B6222A4E929E0ACD10E910758E" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">In general</span>.—No Federal funds that are considered direct spending and provided to carry out a State plan under title XIX of the Social Security Act or a waiver of such a plan shall be used to make payments to a prohibited entity for items and services furnished during the 1-year period beginning on the date of the enactment of this Act, including any payments made directly to the prohibited entity or under a contract or other arrangement between a State and a covered organization. </span>
                <a id="H6D095D897A064A338A641A769AF24BC1" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">Definitions</span>.—In this section:
                    <a id="HE6B22E1952D94608A410E6ACAF5CEE71" />
                    <span class="lbexIndentParagraph">(1) PROHIBITED ENTITY.—The term “prohibited entity” means an entity, including its affiliates, subsidiaries, successors, and clinics—
                        <a id="H6FC510BDCECA4FCABC88EC2E428DE185" />
                        <span class="lbexIndentSubpar">(A) that, as of the first day of the first quarter beginning after the date of enactment of this Act—
                            <a id="H608232A6175D4CD4BC1E3FB45CABE32C" />
                            <span class="lbexIndentClause">(i) is an organization described in <a
                                href="https://uscode.house.gov/quicksearch/get.plx?title=26&amp;section=501"
                                class="external"
                                target="_blank"
                            >section 501(c)(3)</a> of the Internal Revenue Code of 1986 and exempt from tax under section 501(a) of such Code;</span>
                            <a id="H589B5CE0C627419280D75FB2BB5AC0FB" />
                            <span class="lbexIndentClause">(ii) is an essential community provider described in section <a href="/45/156/Subpart-C/#156-235">156.235</a> of title 45, Code of Federal Regulations (as in effect on the date of enactment of this Act), that is primarily engaged in family planning services, reproductive health, and related medical care; and</span>
                            <a id="H7F2D87B146174050A9A298AB579A3CD5" />
                            <span class="lbexIndentClause">(iii) provides for abortions, other than an abortion—
                                <a id="H1BFF52D791314DCD94FA987EF6767212" />
                                <span class="lbexIndentSubclause">(I) if the pregnancy is the result of an act of rape or incest; or</span>
                                <a id="H3276284F5C9C4A14A04361BCB7172771" />
                                <span class="lbexIndentSubclause">(II) in the case where a woman suffers from a physical disorder, physical injury, or physical illness, including a life-endangering physical condition caused by or arising from the pregnancy itself, that would, as certified by a physician, place the woman in danger of death unless an abortion is performed; and</span>
                            </span>
                        </span>
                        <a id="H9ED4D1C14CC84620A3DF5FA932CE0754" />
                        <span class="lbexIndentSubpar">(B) for which the total amount of Federal and State expenditures under the Medicaid program under title XIX of the Social Security Act for medical assistance furnished in fiscal year 2023 made directly, or by a covered organization, to the entity or to any affiliates, subsidiaries, successors, or clinics of the entity, or made to the entity or to any affiliates, subsidiaries, successors, or clinics of the entity as part of a nationwide health care provider network, exceeded $800,000.</span>
                    </span>
                </span>

                <a id="HD88761F8ED344F4983817A5D46050378" />
                <span class="lbexIndentParagraph">(2) DIRECT SPENDING.—The term “direct spending” has the meaning given that term under section 250(c) of the Balanced Budget and Emergency Deficit Control Act of 1985 (<a
                    href="https://uscode.house.gov/quicksearch/get.plx?title=2&amp;section=900"
                    class="external"
                    target="_blank"
                >2 U.S.C. 900(c)</a>).</span>

                <a id="HD46C0855B83542C4B5E1F07AC65444C4" />
                <span class="lbexIndentParagraph">(3) COVERED ORGANIZATION.—The term “covered organization” means a managed care entity (as defined in section 1932(a)(1)(B) of the Social Security Act (<a
                    href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396u-2&num=0&edition=prelim#substructure-location_a_1_B"
                    class="external"
                    target="_blank"
                >42 U.S.C. 1396u–2(a)(1)(B)</a>)) or a prepaid inpatient health plan or prepaid ambulatory health plan (as such terms are defined in section 1903(m)(9)(D) of such Act (<a
                    href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396b&num=0&edition=prelim#substructure-location_m_9_D"
                    class="external"
                    target="_blank"
                >42 U.S.C. 1396b(m)(9)(D)</a>)).</span>

                <a id="HB3D54CA27A1A43199BB46535DA7D0DD6" />
                <span class="lbexIndentParagraph">(4) STATE.—The term “State” has the meaning given such term in section 1101 of the Social Security Act (<a
                    href="https://uscode.house.gov/quicksearch/get.plx?title=42&amp;section=1301"
                    class="external"
                    target="_blank"
                >42 U.S.C. 1301</a>).</span>

                <a id="H7E92C3D050394B7CA51BBA5B51CA775E" />
                <span class="lbexIndent">(c)
                    <span class="lbexSectionLevelOLCnuclear">Implementation funding</span>.—For the purposes of carrying out this section, there are appropriated, out of any monies in the Treasury not otherwise appropriated, to the Administrator of the Centers for Medicare &amp; Medicaid Services, $1,000,000 for fiscal year 2026, to remain available until expended.</span>
                <span id="H33AAEB14AE494C8981C870486D3E3901" />

                <a id="toc-H33AAEB14AE494C8981C870486D3E3901" href="#H33AAEB14AE494C8981C870486D3E3901">
                    <span class="lbexSubChapterLevelOLC">Subchapter C — Stopping abusive financing practices</span>
                </a>

                <span class="lbexHang">
                    <a id="toc-H027BCCE030064EC1801736510E3BFF79" href="#H027BCCE030064EC1801736510E3BFF79">
                        <span class="lbexHangWithMargin">
                            <span id="H027BCCE030064EC1801736510E3BFF79" />
                            <span class="lbexSectionlevelOLC">Sec. 71114. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Sunsetting increased FMAP incentive</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <span class="lbexIndent">
                    <span class="lbexIndentSectionText">Section 1905(ii)(3) of the Social Security Act (<a
                        href="https://uscode.house.gov/quicksearch/get.plx?title=42&amp;section=1396d"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396d(ii)(3)</a>) is amended—</span> <!-- Did not update this link because the target doesn't work correctly on the US Code page -->
                </span>
                <a id="HD2439E0C48C04FDE8FE8FCE60D804E7A" />
                <span class="lbexIndentParagraph">(1) by striking “which has not” and inserting the following: <span class="annotated-text">“which—</span>
                    <a id="HD95C82A823C2440EA841288A92B1A3D2" />
                    <span class="lbexIndentSubpar"><span class="annotated-text">“(A) has not”</span>; </span>
                </span>

                <a id="H07790A8094C94E159B2B4E0A0C33CCEA" />
                <span class="lbexIndentParagraph">(2) in subparagraph (A), as so inserted, by striking the period at the end and inserting <span class="annotated-text">“; and”</span>; and</span>

                <a id="H52643300F54D4B7F8442FDB4B4B6A9F3" />
                <span class="lbexIndentParagraph">(3) by adding at the end the following new subparagraph:
                    <span class="ul">
                        <a id="H36AE516BC3E34154A83C394837C26012" />
                        <span class="lbexIndentSubpar annotated-text">“(B) begins to expend amounts for all such individuals prior to January 1, 2026.”.</span>
                    </span>
                </span>

                <span class="lbexHang">
                    <a id="toc-HC5CF4567712D420786321990FC6F05A3" href="#HC5CF4567712D420786321990FC6F05A3">
                        <span class="lbexHangWithMargin">
                            <span id="HC5CF4567712D420786321990FC6F05A3" />
                            <span class="lbexSectionlevelOLC">Sec. 71115. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Provider taxes</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="HD1668A87651A42AEBD33453570189B7A" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">Change in threshold for hold harmless provision of broad-based health care related taxes</span>.—Section 1903(w)(4) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396b&num=0&edition=prelim#substructure-location_w_4"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396b(w)(4)</a>) is amended—
                    <a id="H613FD416BE0242AA9BA15137AB8AB252" />
                    <span class="lbexIndentParagraph">(1) in subparagraph (C)(ii), by inserting “, and for fiscal years beginning on or after October 1, 2026, the applicable percent determined under subparagraph (D) shall be substituted for
                        <span class="lbexThinSpace" />‘6 percent’ each place it appears” after “each place it appears”; and</span>
                </span>
                <a id="HBAD00B00430C4973AE151228A6710CCE" />
                <span class="lbexIndentParagraph">(2) by inserting after subparagraph (C)(ii), the following new subparagraph:
                    <span class="lbexIndentSubsection">
                        <a id="H20D36E644A5540F5BB7E376E7A0ED2C1" />
                        <span class="lbexIndentParagraph">“(D)<a id="H7B64F6DB41074587B2D2EFF4CB2DB9C1" />(i) For purposes of subparagraph (C)(ii), the applicable percent determined under this subparagraph is—
                            <a id="HDF81F1D064A847118AB152C689CB7CD8" />
                            <span class="lbexIndentSubpar">“(I) in the case of a non-expansion State or unit of local government in such State and a class of health care items or services described in section <a href="/42/433/Subpart-B/#433-56-a">433.56(a)</a> of title 42, Code of Federal Regulations (as in effect on May 1, 2025)—
                                <a id="HF7E6031DCDD345F09E8D67BB87A018EB" />
                                <span class="lbexIndentClause">“(aa) if, on the date of enactment of this subparagraph, the non-expansion State or unit of local government in such State has enacted a tax and imposes such tax on such class and the Secretary determines that the tax is within the hold harmless threshold as of that date, the applicable percent of net patient revenue attributable to such class that has been so determined; and</span>
                                <a id="H3B56C17EC18642CAB67D1CED226B2213" />
                                <span class="lbexIndentClause">“(bb) if, on the date of enactment of this subparagraph, the non-expansion State or unit of local government in such State has not enacted or does not impose a tax with respect to such class, 0 percent; and</span>
                            </span>
                            <a id="H33CC9AADE0694967B28F38ADA6724BDA" />
                            <span class="lbexIndentSubpar">“(II) in the case of an expansion State or unit of local government in such State and a class of health care items or services described in section <a href="/42/433/Subpart-B/#433-56-a">433.56(a)</a> of title 42, Code of Federal Regulations (as in effect on May 1, 2025), subject to clause (iv)—
                                <a id="H475F82BE8791418DA85C5A6050B87FAA" />
                                <span class="lbexIndentClause">“(aa) if, on the date of enactment of this subparagraph, the expansion State or unit of local government in such State has enacted a tax and imposes such tax on such class and the Secretary determines that the tax is within the hold harmless threshold as of that date, the lower of—
                                    <span class="lbexIndentSubclause">“(AA) the applicable percent of net patient revenue attributable to such class that has been so determined; and</span>
                                    <span class="lbexIndentSubclause">“(BB) the applicable percent specified in clause (ii) for the fiscal year; and</span>
                                </span>
                            </span>
                            <a id="H31D4183C227D4FF3AC96CD3170361C8D" />
                            <span class="lbexIndentClause">“(bb) if, on the date of enactment of this subparagraph, the expansion State or unit of local government in such State has not enacted or does not impose a tax with respect to such class, 0 percent.</span>
                        </span>

                        <a id="H9682CC4CB5524664AD922E612D0E6668" />
                        <span class="lbexIndentParagraph">“(ii) For purposes of clause (i)(II)(aa)(BB), the applicable percent is—
                            <a id="H1795ED55DE39419180474C5D289F2512" />
                            <span class="lbexIndentSubpar">“(I) for fiscal year 2028, 5.5 percent;</span>
                            <a id="HE5B85442C03542B4A0A59778599CDA7E" />
                            <span class="lbexIndentSubpar">“(II) for fiscal year 2029, 5 percent;</span>

                            <a id="H27D124A726864BD99F79E6AFB9B165F5" />
                            <span class="lbexIndentSubpar">“(III) for fiscal year 2030, 4.5 percent;</span>

                            <a id="H6EF9FF5ECCD04B9EAC5AA5141100D135" />
                            <span class="lbexIndentSubpar">“(IV) for fiscal year 2031, 4 percent; and</span>

                            <a id="HB4A97C987A814518AE30249E41A45DD3" />
                            <span class="lbexIndentSubpar">“(V) for fiscal year 2032 and each subsequent fiscal year, 3.5 percent.</span>
                        </span>

                        <a id="H0BE4245A202F4BDFA3B58473D164FD77" />
                        <span class="lbexIndentParagraph">“(iii) For purposes of clause (i):
                            <a id="H6C67C761B200451BBE6763A113A8C37C" />
                            <span class="lbexIndentSubpar">“(I) EXPANSION STATE.—The term ‘expansion State’ means a State that, beginning on January 1, 2014, or on any date thereafter, elects to provide medical assistance to all individuals described in section 1902(a)(10)(A)(i)(VIII) under the State plan under this title or under a waiver of such plan.</span>
                            <a id="H5569636C1AFD4C2D82534554D7EF807B" />
                            <span class="lbexIndentSubpar">“(II) NON-EXPANSION STATE.—The term ‘non-expansion State’ means a State that is not an expansion State.</span>
                        </span>

                        <a id="HC3E6BE91A4DD4081B90C2CB16E1B27A9" />
                        <span class="lbexIndentParagraph">“(iv) In the case of a tax of an expansion State or unit of local government in such State in effect on the date of enactment of this clause, that applies to a class of health care items or services that is described in paragraph (3) or (4) of section <a href="/42/433/Subpart-B/#433-56-a">433.56(a)</a> of title 42, Code of Federal Regulations (as in effect on May 1, 2025), and for which, on such date of enactment, is within the hold harmless threshold (as determined by the Secretary), the applicable percent of net patient revenue attributable to such class that has been so determined shall apply for a fiscal year instead of the applicable percent specified in clause (ii) for the fiscal year.”.</span>
                    </span>
                </span>

                <a id="H27E5FA086CCB4CF89AB296D727EF7A89" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">Non-application to territories</span>.—The amendments made by this section shall only apply with respect to a State that is 1 of the 50 States or the District of Columbia.</span>
                <a id="HC2BCE723D741464FB0CB0B140B9097B1" />
                <span class="lbexIndent">(c)
                    <span class="lbexSectionLevelOLCnuclear">Implementation funding</span>.—For the purposes of carrying out the provisions of, and the amendments made by, this section, there are appropriated, out of any monies in the Treasury not otherwise appropriated, to the Administrator of the Centers for Medicare &amp; Medicaid Services, $20,000,000 for fiscal year 2026, to remain available until expended.</span>

                <span class="lbexHang">
                    <a id="toc-H5095A31A390141E1AF3A2DAD32DD6532" href="#H5095A31A390141E1AF3A2DAD32DD6532">
                        <span class="lbexHangWithMargin">
                            <span id="H5095A31A390141E1AF3A2DAD32DD6532" />
                            <span class="lbexSectionlevelOLC">Sec. 71116. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">State directed payments</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="H6081C5C3FF704314AFF57BA411E26DDE" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">In general</span>.—Subject to subsection (b), the Secretary of Health and Human Services (in this section referred to as the Secretary) shall revise section <a href="/42/438/Subpart-A/#438-6-i-2-iii">438.6(c)(2)(iii)</a> of title 42, Code of Federal Regulations (or a successor regulation) such that, with respect to a payment described in such section made for a service furnished during a rating period beginning on or after the date of the enactment of this Act, the total payment rate for such service is limited to—
                    <a id="HC7FA119FA48845338BE885CBFF7EB408" />
                    <span class="lbexIndentParagraph">(1) in the case of a State that provides coverage to all individuals described in section 1902(a)(10)(A)(i)(VIII) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396a&num=0&edition=prelim#substructure-location_a_10_A_i_VIII"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396a(a)(10)(A)(i)(VIII)</a>) that is equivalent to minimum essential coverage (as described in <a
                        href="https://uscode.house.gov/quicksearch/get.plx?title=26&amp;section=5000A"
                        class="external"
                        target="_blank"
                    >section 5000A(f)(1)(A)</a> of the Internal Revenue Code of 1986 and determined in accordance with standards prescribed by the Secretary in regulations) under the State plan (or waiver of such plan) of such State under title XIX of such Act, 100 percent of the specified total published Medicare payment rate (or, in the absence of a specified total published Medicare payment rate, the payment rate under a Medicaid State plan (or under a waiver of such plan)); or</span>
                    <a id="H68132C34E5FD46DEA1334425F00FCD72" />
                    <span class="lbexIndentParagraph">(2) in the case of a State other than a State described in paragraph (1), 110 percent of the specified total published Medicare payment rate (or, in the absence of a specified total published Medicare payment rate, the payment rate under a Medicaid State plan (or under a waiver of such plan)).</span>
                </span>
                <a id="HDF8733C85AF248F388EEB66529058959" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">Grandfathering certain payments</span>.—In the case of a payment described in section <a href="/42/438/Subpart-A/#438-6-i-2-iii">438.6(c)(2)(iii)</a> of title 42, Code of Federal Regulations (or a successor regulation) for which written prior approval (or a good faith effort to receive such approval, as determined by the Secretary) was made before May 1, 2025, or a payment described in such section for a rural hospital (as defined in subsection (d)(2)) for which written prior approval (or a good faith effort to receive such approval, as determined by the Secretary) was made by the date of enactment of this Act, for the rating period occurring within 180 days of the date of the enactment of this Act, or a payment so described for such rating period for which a completed preprint was submitted to the Secretary prior to the date of enactment of this Act, beginning with the rating period on or after January 1, 2028, the total amount of such payment shall be reduced by 10 percentage points each year until the total payment rate for such service is equal to the rate for such service specified in subsection (a).</span>
                <a id="HE5D55700A09E4588B22AD16BF89FE95D" />
                <span class="lbexIndent">(c)
                    <span class="lbexSectionLevelOLCnuclear">Treatment of expansion states</span>.—The revisions described in subsection (a) shall provide that, with respect to a State that begins providing the coverage described in paragraph (1) of such subsection on or after the date of the enactment of this Act, the limitation described in such paragraph shall apply to such State with respect to a payment described in section <a href="/42/438/Subpart-A/#438-6-i-2-iii">438.6(c)(2)(iii)</a> of title 42, Code of Federal Regulations (or a successor regulation) for a service furnished during a rating period beginning on or after the date of enactment of this Act.</span>
                <a id="HBEA8D8254C8D4E6FA9A9BB30161AF637" />
                <span class="lbexIndent">(d)
                    <span class="lbexSectionLevelOLCnuclear">Definitions</span>.—In this section:
                    <a id="H0FA8895A2CF44F0F8F20C1B2127F7710" />
                    <span class="lbexIndentParagraph">(1) RATING PERIOD.—The term “rating period” has the meaning given such term in section <a href="/42/438/Subpart-A/#438-2">438.2</a> of title 42, Code of Federal Regulations (or a successor regulation).</span>
                </span>
                <a id="H853967811D0341A9BBAD7278E4F65755" />
                <span class="lbexIndentParagraph">(2) RURAL HOSPITAL.—The term “rural hospital” means the following:
                    <a id="HB4B48C2C98234AA180146381EB0C9DE7" />
                    <span class="lbexIndentSubpar">(A) A subsection (d) hospital (as defined in paragraph (1)(B) of section 1886(d) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1395ww&num=0&edition=prelim#substructure-location_d"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1395ww(d)</a>)) that—
                        <a id="H28455D3F532248ED87C4D9CDD20A39DE" />
                        <span class="lbexIndentClause">(i) is located in a rural area (as defined in paragraph (2)(D) of such section); </span>
                        <a id="HB42272FC99CE4B3F88E4380D89F8B993" />
                        <span class="lbexIndentClause">(ii) is treated as being located in a rural area pursuant to paragraph (8)(E) of such section; or </span>
                        <a id="H5FBFCFB21723476C85468AFB25F4CB75" />
                        <span class="lbexIndentClause">(iii) is located in a rural census tract of a metropolitan statistical area (as determined under the most recent modification of the Goldsmith Modification, originally published in the Federal Register on February 27, 1992 (<a
                            href="https://www.federalregister.gov/citation/57-FR-6725"
                            class="external"
                            target="_blank"
                        >57 Fed. Reg. 6725</a>)).</span>
                    </span>

                    <a id="HCE59402B78ED4216834F2661B7AE124E" />
                    <span class="lbexIndentSubpar">(B) A critical access hospital (as defined in section 1861(mm)(1) of such Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1395x&num=0&edition=prelim#substructure-location_mm_1"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1395x(mm)(1)</a>)).</span>

                    <a id="H469A0CCA86A648A08AC5D213366E217D" />
                    <span class="lbexIndentSubpar">(C) A sole community hospital (as defined in section 1886(d)(5)(D)(iii) of such Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1395ww&num=0&edition=prelim#substructure-location_d_5_D_iii"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1395ww(d)(5)(D)(iii)</a>)).</span>

                    <a id="HCB61C01C4F9041ED89418D3EB562E5C3" />
                    <span class="lbexIndentSubpar">(D) A Medicare-dependent, small rural hospital (as defined in section 1886(d)(5)(G)(iv) of such Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1395ww&num=0&edition=prelim#substructure-location_d_5_G_iv"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1395ww(d)(5)(G)(iv)</a>)). </span>

                    <a id="H141EDCA002E14CDE8BFBC3738961EB39" />
                    <span class="lbexIndentSubpar">(E) A low-volume hospital (as defined in section 1886(d)(12)(C) of such Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1395ww&num=0&edition=prelim#substructure-location_d_12_C"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1395ww(d)(12)(C)</a>)).</span>

                    <a id="H99E320165DC64DC7B4E8DAEBFC4F42F1" />
                    <span class="lbexIndentSubpar">(F) A rural emergency hospital (as defined in section 1861(kkk)(2) of such Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1395x&num=0&edition=prelim#substructure-location_kkk_2"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1395x(kkk)(2)</a>)).</span>
                </span>

                <a id="H6851A087D44D4B6089749F3C3036FA8D" />
                <span class="lbexIndentParagraph">(3) STATE.—The term “State” means 1 of the 50 States or the District of Columbia.</span>

                <a id="HBAF440488AE74136B66521A9418E5747" />
                <span class="lbexIndentParagraph">(4) TOTAL PUBLISHED MEDICARE PAYMENT RATE.—The term “total published Medicare payment rate” has the meaning given to such term in section 438.6(a) of title 42, Code of Federal Regulations (or a successor regulation).</span>

                <a id="H9334788623AB48D59AA5F48A7931A73A" />
                <span class="lbexIndentParagraph">(5) WRITTEN PRIOR APPROVAL.—The term “written prior approval” has the meaning given to such term in section <a href="/42/438/Subpart-A/#438-6-i-2-i">438.6(c)(2)(i)</a> of title 42, Code of Federal Regulations (or a successor regulation).</span>

                <a id="HC6803D86FB4C4A04AD9B3927CFBED342" />
                <span class="lbexIndent">(e)
                    <span class="lbexSectionLevelOLCnuclear">Funding</span>.—There are appropriated out of any monies in the Treasury not otherwise appropriated $7,000,000 for each of fiscal years 2026 through 2033 for purposes of carrying out this section, to remain available until expended.</span>

                <span class="lbexHang">
                    <a id="toc-HFC9712978086448A884AD4DA6242CFF0" href="#HFC9712978086448A884AD4DA6242CFF0">
                        <span class="lbexHangWithMargin">
                            <span id="HFC9712978086448A884AD4DA6242CFF0" />
                            <span class="lbexSectionlevelOLC">Sec. 71117. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Requirements regarding waiver of uniform tax requirement for Medicaid provider tax</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="H946D195148204135A731BDE8117729B1" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">In general</span>.—Section 1903(w) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396b&num=0&edition=prelim#substructure-location_w"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396b(w)</a>) is amended—
                    <a id="H896B2C9E4844473CA7E37EFF871EF795" />
                    <span class="lbexIndentParagraph">(1) in paragraph (3)(E), by inserting after clause (ii)(II) the following new clause:
                        <span class="lbexIndentSubsection">
                            <a id="HDB84925810DC49BAB9F573C4A3D00F45" />
                            <span class="lbexIndentParagraph">“(iii) For purposes of clause (ii)(I), a tax is not considered to be generally redistributive if any of the following conditions apply:
                                <a id="H03B8A44D85AA40949002B8C098AAAEE8" />
                                <span class="lbexIndentParagraph">“(I) Within a permissible class, the tax rate imposed on any taxpayer or tax rate group (as defined in paragraph (7)(J)) explicitly defined by its relatively lower volume or percentage of Medicaid taxable units (as defined in paragraph (7)(H)) is lower than the tax rate imposed on any other taxpayer or tax rate group explicitly defined by its relatively higher volume or percentage of Medicaid taxable units.</span>
                            </span>
                            <a id="HEE667679F8A44D00AE18E0B4FCDDBDED" />
                            <span class="lbexIndentParagraph">“(II) Within a permissible class, the tax rate imposed on any taxpayer or tax rate group (as so defined) based upon its Medicaid taxable units (as so defined) is higher than the tax rate imposed on any taxpayer or tax rate group based upon its non-Medicaid taxable unit (as defined in paragraph (7)(I)).</span>
                            <a id="HD38362D5B66F48608C0D9DB6B705B431" />
                            <span class="lbexIndentParagraph">“(III) The tax excludes or imposes a lower tax rate on a taxpayer or tax rate group (as so defined) based on or defined by any description that results in the same effect as described in subclause (I) or (II) for a taxpayer or tax rate group. Characteristics that may indicate such type of exclusion include the use of terminology to establish a tax rate group—
                                <a id="H84E204309ADE408E861ADFBDD103BA7A" />
                                <span class="lbexIndentSubpar">“(aa) based on payments or expenditures made under the program under this title without mentioning the term ‘Medicaid’ (or any similar term) to accomplish the same effect as described in subclause (I) or (II); or</span>
                                <a id="HA149EE9707124B03975508A0CCD79871" />
                                <span class="lbexIndentSubpar">“(bb) that closely approximates a taxpayer or tax rate group under the program under this title, to the same effect as described in subclause (I) or (II).”; and</span>
                            </span>
                        </span>
                    </span>
                </span>

                <a id="H1F7BB46D64CF494995F477494610E500" />
                <span class="lbexIndentParagraph">(2) in paragraph (7), by adding at the end the following new subparagraphs:
                    <span class="lbexIndentSubsection">
                        <a id="H38D5FD1A89AB49B1B8A826F3DEAB9E69" />
                        <span class="lbexIndentParagraph">“(H) The term ‘Medicaid taxable unit’ means a unit that is being taxed within a health care related tax that is applicable to the program under this title. Such term includes a unit that is used as the basis for—
                            <a id="H507BE300DFF644A09B1F6742CBE72281" />
                            <span class="lbexIndentSubpar">“(i) payment under the program under this title (such as Medicaid bed days);</span>
                            <a id="HBD128F1E08234D78B5923FBEB928ED7E" />
                            <span class="lbexIndentSubpar">“(ii) Medicaid revenue;</span>
                            <a id="HF4400ED94B994D478D523B5FB326E862" />
                            <span class="lbexIndentSubpar">“(iii) costs associated with the program under this title (such as Medicaid charges, claims, or expenditures); and</span>
                            <a id="H94059654E46E4F91AC99750788F30347" />
                            <span class="lbexIndentSubpar">“(iv) other units associated with the program under this title, as determined by the Secretary.</span>
                        </span>

                        <a id="HCADD595F07A54FA6A8054198E164327D" />
                        <span class="lbexIndentParagraph">“(I) The term ‘non-Medicaid taxable unit’ means a unit that is being taxed within a health care related tax that is not applicable to the program under this title. Such term includes a unit that is used as the basis for—
                            <a id="H08032CDAE03C4AA6BF1C0A38D7B91F7B" />
                            <span class="lbexIndentSubpar">“(i) payment by non-Medicaid payers (such as non-Medicaid bed days);</span>
                            <a id="HA5ACC9EB52A84CCAAA09100779C9AE53" />
                            <span class="lbexIndentSubpar">“(ii) non-Medicaid revenue;</span>

                            <a id="H6261AA0436BA404A843D055D44E7D050" />
                            <span class="lbexIndentSubpar">“(iii) costs that are not associated with the program under this title (such as non-Medicaid charges, non-Medicaid claims, or non-Medicaid expenditures); and</span>

                            <a id="HE1C21B132F2647419AA92CACAAEC8637" />
                            <span class="lbexIndentSubpar">“(iv) other units not associated with the program under this title, as determined by the Secretary.</span>
                        </span>

                        <a id="H5137386EA3604F4C9DD11528F9F5930D" />
                        <span class="lbexIndentParagraph">“(J) The term ‘tax rate group’ means a group of entities contained within a permissible class of a health care related tax that are taxed at the same rate.”.</span>
                    </span>
                </span>

                <a id="HA10AED42DB914622A660F6BA65C2AA3B" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">Non-application to territories</span>.—The amendments made by this section shall only apply with respect to a State that is 1 of the 50 States or the District of Columbia.</span>
                <a id="HFBCA54ACCF6E4D2DAE7F79F7BE4C6ED4" />
                <span class="lbexIndent">(c)
                    <span class="lbexSectionLevelOLCnuclear">Effective date</span>.—The amendments made by this section shall take effect upon the date of enactment of this Act, subject to any applicable transition period determined appropriate by the Secretary of Health and Human Services, not to exceed 3 fiscal years.</span>

                <span class="lbexHang">
                    <a id="toc-H3DFC92C358834F5B82DE8AB81465692A" href="#H3DFC92C358834F5B82DE8AB81465692A">
                        <span class="lbexHangWithMargin">
                            <span id="H3DFC92C358834F5B82DE8AB81465692A" />
                            <span class="lbexSectionlevelOLC">Sec. 71118. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Requiring budget neutrality for Medicaid demonstration projects under section 1115</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="H05A306D8A48742AE85C93943E85D9BFD" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">In general</span>.—Section 1115 of the Social Security Act (<a
                        href="https://uscode.house.gov/quicksearch/get.plx?title=42&amp;section=1315"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1315</a>) is amended by adding at the end the following new subsection:
                    <span class="lbexIndent">
                        <a id="H6F0FA9A5E62A4810A41334871123A247" />
                        <span class="lbexIndentSubsection">
                            <span class="lbexIndentParagraph">“(g)
                                <span class="lbexSectionLevelOLCnuclear">Requirement of budget neutrality for Medicaid demonstration projects</span>.—
                                <a id="HCE35A72C9ABE4327B977E3055671EDF7" />
                                <span class="lbexIndentParagraph">“(1) IN GENERAL.—Beginning January 1 2027, the Secretary may not approve an application for (or renewal or amendment of) an experimental, pilot, or demonstration project undertaken under subsection (a) to promote the objectives of title XIX in a State (in this subsection referred to as a ‘Medicaid demonstration project’) unless the Chief Actuary for the Centers for Medicare &amp; Medicaid Services certifies that such project, or, in the case of a renewal, the duration of the preceding waiver, is not expected to result in an increase in the amount of Federal expenditures compared to the amount that such expenditures would otherwise be in the absence of such project. For purposes of this subsection, expenditures for the coverage of populations and services that the State could have otherwise provided through its Medicaid State plan or other authority under title XIX, including expenditures that could be made under such authority but for the provision of such services at a different site of service than authorized under such State plan or other authority, shall be considered expenditures in the absence of such a project.</span>
                                <a id="H6273450F6A7C4E0AA6AF422F6CD1E5ED" />
                                <span class="lbexIndentParagraph">“(2) TREATMENT OF SAVINGS.—In the event that expenditures with respect to a State under a Medicaid demonstration project are, during an approval period for such project, less than the amount of such expenditures that would have otherwise been made in the absence of such project, the Secretary shall specify the methodology to be used with respect to the subsequent approval period for such project for purposes of taking the difference between such expenditures into account.”.</span>
                            </span>
                        </span>
                    </span>
                </span>

                <a id="HC651C1F15D254E90AFA22CC14D3D8207" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">Implementation funding</span>.—For the purposes of carrying out the provisions of, and the amendments made by, this section, there are appropriated, out of any monies in the Treasury not otherwise appropriated, to the Administrator of the Centers for Medicare &amp; Medicaid Services, $5,000,000 for each of fiscal years 2026 and 2027, to remain available until expended.</span>
                <span id="H41B4BE6053784F329BB924FD89F29721" />

                <a id="toc-H41B4BE6053784F329BB924FD89F29721" href="#H41B4BE6053784F329BB924FD89F29721">
                    <span class="lbexSubChapterLevelOLC">Subchapter D — Increasing personal accountability</span>
                </a>

                <span class="lbexHang">
                    <a id="toc-HE10C293F1AD14FEE88FED90835BFBB2D" href="#HE10C293F1AD14FEE88FED90835BFBB2D">
                        <span class="lbexHangWithMargin">
                            <span id="HE10C293F1AD14FEE88FED90835BFBB2D" />
                            <span class="lbexSectionlevelOLC">Sec. 71119. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Requirement for States to establish Medicaid community engagement requirements for certain individuals</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="H2B46E3225A4B47F5815B7CBC456D620D" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">In general</span>.—Section 1902 of the Social Security Act (<a
                        href="https://uscode.house.gov/quicksearch/get.plx?title=42&amp;section=1396a"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396a</a>), as amended by sections 71103 and 71104, is further amended by adding at the end the following new subsection:

                    <a id="H8E766BAEAC77476D94E39EC929595539" />
                    <span class="lbexIndentSubsection">
                        <span class="lbexIndentParagraph">“(xx)
                            <span class="lbexSectionLevelOLCnuclear">Community engagement requirement for applicable individuals</span>.—
                            <a id="HEE8799D1FF664550B27FE20B048550DA" />

                            <span class="lbexIndentParagraph">
                                “(1) IN GENERAL.—Except as provided in paragraph (11), beginning not later than the first day of the first quarter that begins after December 31, 2026, or, at the option of the State under a waiver or demonstration project under section 1115 or the State plan, such earlier date as the State may specify, subject to the succeeding provisions of this subsection, a State shall provide, as a condition of eligibility for medical assistance for an applicable individual, that such individual is required to demonstrate community engagement under <a href="#H658FE037F1624A438230B2B24A421EB5">paragraph (2)</a>—
                                <a id="H86230D4AD5224BBC8938A0B2A7BFE363" />
                                <span class="lbexIndentSubpar">“(A) in the case of an applicable individual who has filed an application for medical assistance under a State plan (or a waiver of such plan) under this title, for 1 or more but not more than 3 (as specified by the State) consecutive months immediately preceding the month during which such individual applies for such medical assistance; and</span>
                                <a id="HE9BC391A19C748B3982E32641FBC486A" />
                                <span class="lbexIndentSubpar">“(B) in the case of an applicable individual enrolled and receiving medical assistance under a State plan (or under a waiver of such plan) under this title, for 1 or more (as specified by the State) months, whether or not consecutive—
                                    <a id="HD4866F89A25A41159BCE4A7C539CDAA8" />
                                    <span class="lbexIndentClause">“(i) during the period between such individual’s most recent determination (or redetermination, as applicable) of eligibility and such individual’s next regularly scheduled redetermination of eligibility (as verified by the State as part of such regularly scheduled redetermination of eligibility); or</span>
                                    <a id="H9DA8448859E34759A615F7AE5337DE25" />
                                    <span class="lbexIndentClause">“(ii) in the case of a State that has elected under <a href="#H85A521B791134FE7B6BBF57C6400EA1A">paragraph (4)</a> to conduct more frequent verifications of compliance with the requirement to demonstrate community engagement, during the period between the most recent and next such verification with respect to such individual.</span>
                                </span>
                            </span>



                            <a id="H658FE037F1624A438230B2B24A421EB5" />
                            <span class="lbexIndentParagraph">“(2) COMMUNITY ENGAGEMENT COMPLIANCE DESCRIBED.—Subject to <a href="#HB95A875567A74FBC9933837B304F0F9C">paragraph (3)</a>, an applicable individual demonstrates community engagement under this paragraph for a month if such individual meets 1 or more of the following conditions with respect to such month, as determined in accordance with criteria established by the Secretary through regulation:
                                <a id="H14BE1DA11CCF44FE8DF3B3A438C60469" />
                                <span class="lbexIndentSubpar">“(A) The individual works not less than 80 hours.</span>

                                <a id="HF6E1C6D1856D4823A4D6A148F0E787E1" />
                                <span class="lbexIndentSubpar">“(B) The individual completes not less than 80 hours of community service.</span>

                                <a id="HAD9C7F14080C46A99E46569A41E929C4" />
                                <span class="lbexIndentSubpar">“(C) The individual participates in a work program for not less than 80 hours.</span>

                                <a id="H7A30ED862098412780F8DEB1FF9758D7" />
                                <span class="lbexIndentSubpar">“(D) The individual is enrolled in an educational program at least half-time.</span>

                                <a id="H0A3394E9E1E149038F4E11F0EC1CC27B" />
                                <span class="lbexIndentSubpar">“(E) The individual engages in any combination of the activities described in subparagraphs (A) through (D), for a total of not less than 80 hours.</span>

                                <a id="HEB337B55673C487CB259398A8FAA82AB" />
                                <span class="lbexIndentSubpar">“(F) The individual has a monthly income that is not less than the applicable minimum wage requirement under section 6 of the Fair Labor Standards Act of 1938, multiplied by 80 hours.</span>

                                <a id="H0DF1E2271CF94FE786EF1A1CEF2901C8" />
                                <span class="lbexIndentSubpar">“(G) The individual had an average monthly income over the preceding 6 months that is not less than the applicable minimum wage requirement under section 6 of the Fair Labor Standards Act of 1938 multiplied by 80 hours, and is a seasonal worker, as described in <a
                                    href="https://uscode.house.gov/quicksearch/get.plx?title=26&amp;section=45R"
                                    class="external"
                                    target="_blank"
                                >section 45R(d)(5)(B)</a> of the Internal Revenue Code of 1986 .</span>
                            </span>

                            <a id="HB95A875567A74FBC9933837B304F0F9C" />
                            <span class="lbexIndentParagraph">“(3) EXCEPTIONS.—

                                <a id="H74FC529C00B0461E8AF24E0D3AE2D632" />
                                <span class="lbexIndentSubpar">“(A) MANDATORY EXCEPTION FOR CERTAIN INDIVIDUALS.—The State shall deem an applicable individual to have demonstrated community engagement under <a href="#H658FE037F1624A438230B2B24A421EB5">paragraph (2)</a> for a month, and may elect to not require an individual to verify information resulting in such deeming, if—
                                    <a id="HFF350094FC114651A3F8A19D47EF5998" />
                                    <span class="lbexIndentClause">“(i) for part or all of such month, the individual—
                                        <a id="HFC8EC001D5B642949B32A18F731F8A55" />
                                        <span class="lbexIndentSubclause">“(I) was a specified excluded individual (as defined in <a href="#H5FDC36B12F4B4549AF8155AF1BCC1523">paragraph (9)(A)(ii)</a>); or</span>
                                        <a id="HEECC45B927264D51BD1673FA4055EDF0" />
                                        <span class="lbexIndentSubclause">“(II) was—
                                            <a id="H81A4AE6BE3A34740960B6CD91C12E9FF" />
                                            <span class="lbexIndentItem">“(aa) under the age of 19;</span>
                                            <a id="H9F63B8D7BC614D7C94016FBBC4A23074" />
                                            <span class="lbexIndentItem">“(bb) entitled to, or enrolled for, benefits under part A of title XVIII, or enrolled for benefits under part B of title XVIII; or</span>
                                            <a id="H9DB8A94E9A9B441094FE3D482BDED330" />
                                            <span class="lbexIndentItem">“(cc) described in any of subclauses (I) through (VII) of subsection (a)(10)(A)(i); or</span>
                                        </span>
                                    </span>
                                    <a id="HBA346B4F756B4836BA83F5DCA47691B5" />
                                    <span class="lbexIndentClause">“(ii) at any point during the 3-month period ending on the first day of such month, the individual was an inmate of a public institution. </span>
                                </span>

                                <a id="HB485058E6C304AD0A102EBFDF98F4D45" />
                                <span class="lbexIndentSubpar">“(B) OPTIONAL EXCEPTION FOR SHORT-TERM HARDSHIP EVENTS.—
                                    <a id="H8FBA36F92FF7431FBD96DF1E99D007EB" />
                                    <span class="lbexIndentClause">“(i) IN GENERAL.—The State plan (or waiver of such plan) may provide, in the case of an applicable individual who experiences a short-term hardship event during a month, that the State shall, under procedures established by the State (in accordance with standards specified by the Secretary), in the case of a short-term hardship event described in clause (ii)(II) and, upon the request of such individual, a short-term hardship event described in subclause (I) or (III) of clause (ii), deem such individual to have demonstrated community engagement under paragraph (2) for such month.</span>


                                    <a id="HC240AFF4607C4401B914115D4BE18FA6" />
                                    <span class="lbexIndentClause">“(ii) SHORT-TERM HARDSHIP EVENT DEFINED.—For purposes of this subparagraph, an applicable individual experiences a short-term hardship event during a month if, for part or all of such month—
                                        <a id="H434F1D262BBB485D8AAAC8710E2780A5" />
                                        <span class="lbexIndentSubclause">“(I) such individual receives inpatient hospital services, nursing facility services, services in an intermediate care facility for individuals with intellectual disabilities, inpatient psychiatric hospital services, or such other services of similar acuity (including outpatient care relating to other services specified in this subclause) as the Secretary determines appropriate;</span>

                                        <a id="H48D42CEF8D9C46BEBC8F3679F52DFE32" />
                                        <span class="lbexIndentSubclause">“(II) such individual resides in a county (or equivalent unit of local government)—
                                            <a id="HB275C5553A67417B8A928F849F8DAD02" />
                                            <span class="lbexIndentItem">“(aa) in which there exists an emergency or disaster declared by the President pursuant to the National Emergencies Act or the Robert T. Stafford Disaster Relief and Emergency Assistance Act; or</span>

                                            <a id="H90BEC31EFB6B45DF9816D21B96D3C9D6" />
                                            <span class="lbexIndentItem">“(bb) that, subject to a request from the State to the Secretary, made in such form, at such time, and containing such information as the Secretary may require, has an unemployment rate that is at or above the lesser of—
                                                <span class="lbexIndentSubItem">“(AA) 8 percent; or</span>
                                                <span class="lbexIndentSubItem">“(BB) 1.5 times the national unemployment rate; or</span>
                                            </span>
                                        </span>
                                        <a id="HB84F54A357A148BBBD6808A620A3FB86" />
                                        <span class="lbexIndentSubclause">“(III) such individual or their dependent must travel outside of their community for an extended period of time to receive medical services necessary to treat a serious or complex medical condition (as described in paragraph (9)(A)(ii)(V)(ee)) that are not available within their community of residence.</span>
                                    </span>
                                </span>
                            </span>

                            <a id="H85A521B791134FE7B6BBF57C6400EA1A" />
                            <span class="lbexIndentParagraph">“(4) OPTION TO CONDUCT MORE FREQUENT COMPLIANCE VERIFICATIONS.—With respect to an applicable individual enrolled and receiving medical assistance under a State plan (or a waiver of such plan) under this title, the State shall verify (in accordance with procedures specified by the Secretary) that each such individual has met the requirement to demonstrate community engagement under paragraph (1) during each such individual’s regularly scheduled redetermination of eligibility, except that a State may provide for such verifications more frequently.</span>

                            <a id="H07D5BD178E89401198C51491252D7CC5" />
                            <span class="lbexIndentParagraph">“(5) EX PARTE VERIFICATIONS.—For purposes of verifying that an applicable individual has met the requirement to demonstrate community engagement under paragraph (1), or determining such individual to be deemed to have demonstrated community engagement under paragraph (3), or that an individual is a specified excluded individual under paragraph (9)(A)(ii), the State shall, in accordance with standards established by the Secretary, establish processes and use reliable information available to the State (such as payroll data or payments or encounter data under this title for individuals and data on payments to such individuals for the provision of services covered under this title) without requiring, where possible, the applicable individual to submit additional information.</span>

                            <a id="H773DA85E707A4855AD114EEA058F31EA" />
                            <span class="lbexIndentParagraph">“(6) PROCEDURE IN THE CASE OF NONCOMPLIANCE.—

                                <a id="H54312ABD87BB4772BBADFD040D4C1B01" />
                                <span class="lbexIndentSubpar">“(A) IN GENERAL.—If a State is unable to verify that an applicable individual has met the requirement to demonstrate community engagement under <a href="#HEE8799D1FF664550B27FE20B048550DA">paragraph (1) </a>(including, if applicable, by verifying that such individual was deemed to have demonstrated community engagement under <a href="#HB95A875567A74FBC9933837B304F0F9C">paragraph (3)</a>) the State shall (in accordance with standards specified by the Secretary)—
                                    <a id="HA59F43A261DE4EBFB288059E6372F234" />
                                    <span class="lbexIndentClause">“(i) provide such individual with the notice of noncompliance described in <a href="#HD924CF591B874D348655933DB44B3612">subparagraph (B)</a>;</span>

                                    <a id="HE7E8C93292324AE5ADD456D5F3E76DCC" />
                                    <span class="lbexIndentClause">“(ii)<a id="H1D9AB81CEB714200A21FB56CE45E4E8E" />(I) provide such individual with a period of 30 calendar days, beginning on the date on which such notice of noncompliance is received by the individual, to—
                                        <a id="H84CC79B705F04C8F9130893688B17226" />
                                        <span class="lbexIndentSubclause">“(aa) make a satisfactory showing to the State of compliance with such requirement (including, if applicable, by showing that such individual was or should be deemed to have demonstrated community engagement under <a href="#HB95A875567A74FBC9933837B304F0F9C">paragraph (3)</a>); or</span>
                                        <a id="H5521F2954AA048ADA2EDC3458DA0D273" />
                                        <span class="lbexIndentSubclause">“(bb) make a satisfactory showing to the State that such requirement does not apply to such individual on the basis that such individual does not meet the definition of applicable individual under <a href="#HC4EBE7D0D4884A48A3E91528D51709B3">paragraph (9)(A)</a>; and</span>
                                        <a id="H93A78CB6EA0242F29E9CF2D51770FCD5" />
                                    </span>
                                    <span class="lbexIndentClause">“(II) if such individual is enrolled under the State plan (or a waiver of such plan) under this title, continue to provide such individual with medical assistance during such 30-calendar-day period; and</span>

                                    <a id="H6B3056BEBD4F41F3AC48EB381C681E9A" />
                                    <span class="lbexIndentClause">“(iii) if no such satisfactory showing is made and the individual is not a specified excluded individual described in <a href="#H5FDC36B12F4B4549AF8155AF1BCC1523">paragraph (9)(A)(ii)</a>, deny such individual’s application for medical assistance under the State plan (or waiver of such plan) or, as applicable, disenroll such individual from the plan (or waiver of such plan) not later than the end of the month following the month in which such 30-calendar-day period ends, provided that—
                                        <a id="HBF050C3630DB4C7A8E3FE1D497F780EE" />
                                        <span class="lbexIndentSubclause">“(I) the State first determines whether, with respect to the individual, there is any other basis for eligibility for medical assistance under the State plan (or waiver of such plan) or for another insurance affordability program; and</span>
                                        <a id="HF7C2A7DBD06945DEB9F8A0A5C8B8ECAD" />
                                        <span class="lbexIndentSubclause">“(II) the individual is provided written notice and granted an opportunity for a fair hearing in accordance with subsection (a)(3).</span>
                                    </span>

                                </span>

                                <a id="HD924CF591B874D348655933DB44B3612" />
                                <span class="lbexIndentSubpar">“(B) NOTICE.—The notice of noncompliance provided to an applicable individual under <a href="#HA59F43A261DE4EBFB288059E6372F234">subparagraph (A)(i)</a> shall include information (in accordance with standards specified by the Secretary) on—
                                    <a id="HB39346FEF8BB49CD82A0B70E9C0AEA96" />
                                    <span class="lbexIndentClause">“(i) how such individual may make a satisfactory showing of compliance with such requirement (as described in <a href="#HE7E8C93292324AE5ADD456D5F3E76DCC">subparagraph (A)(ii)</a>) or make a satisfactory showing that such requirement does not apply to such individual on the basis that such individual does not meet the definition of applicable individual under <a href="#HC4EBE7D0D4884A48A3E91528D51709B3">paragraph (9)(A)</a>; and</span>

                                    <a id="H5C35E54E0822407E80BEE897E38ECFE8" />
                                    <span class="lbexIndentClause">“(ii) how such individual may reapply for medical assistance under the State plan (or a waiver of such plan) under this title in the case that such individuals’ application is denied or, as applicable, in the case that such individual is disenrolled from the plan (or waiver).</span>
                                </span>
                            </span>

                            <a id="HD487FAC7EC844574803C13039AB685C8" />
                            <span class="lbexIndentParagraph">“(7) TREATMENT OF NONCOMPLIANT INDIVIDUALS IN RELATION TO CERTAIN OTHER PROVISIONS.—
                                <a id="H2D21542A91EC4FB89F95D02F8E28B6E2" />
                                <span class="lbexIndentSubpar">“(A) CERTAIN FMAP INCREASES.—A State shall not be treated as not providing medical assistance to all individuals described in section 1902(a)(10)(A)(i)(VIII), or as not expending amounts for all such individuals under the State plan (or waiver of such plan), solely because such an individual is determined ineligible for medical assistance under the State plan (or waiver) on the basis of a failure to meet the requirement to demonstrate community engagement under <a href="#HEE8799D1FF664550B27FE20B048550DA">paragraph (1)</a>.</span>
                                <a id="H75313C7D56A34AA6B2E121F20CE90BC0" />
                                <span class="lbexIndentSubpar">“(B) OTHER PROVISIONS.—For purposes of <a
                                    href="https://uscode.house.gov/quicksearch/get.plx?title=26&amp;section=36B"
                                    class="external"
                                    target="_blank"
                                >section 36B(c)(2)(B)</a> of the Internal Revenue Code of 1986, an individual shall be deemed to be eligible for minimum essential coverage described in section 5000A(f)(1)(A)(ii) of such Code for a month if such individual would have been eligible for medical assistance under a State plan (or a waiver of such plan) under this title but for a failure to meet the requirement to demonstrate community engagement under <a href="#HEE8799D1FF664550B27FE20B048550DA">paragraph (1)</a>.</span>
                            </span>

                            <a id="H8D7E247379FC4D4B99055E839DFAFEF6" />
                            <span class="lbexIndentParagraph">“(8) OUTREACH.—
                                <a id="H21911A424EB74727A14FA0353739EF34" />
                                <span class="lbexIndentSubpar">“(A) IN GENERAL.—In accordance with standards specified by the Secretary, beginning not later than the date that precedes December 31, 2026 (or, if the State elects under paragraph (1) to specify an earlier date, such earlier date) by the number of months specified by the State under paragraph (1)(A) plus 3 months, and periodically thereafter, the State shall notify applicable individuals enrolled under a State plan (or waiver) under this title of the requirement to demonstrate community engagement under this subsection. Such notice shall include information on—
                                    <a id="HE765C23614434CB3A13C5F2126755076" />
                                    <span class="lbexIndentClause">“(i) how to comply with such requirement, including an explanation of the exceptions to such requirement under <a href="#HB95A875567A74FBC9933837B304F0F9C">paragraph (3)</a> and the definition of the term ‘applicable individual’ under <a href="#HC4EBE7D0D4884A48A3E91528D51709B3">paragraph (9)(A);</a>
                                    </span>
                                    <a id="H17C3B5181B664B028910B1EF30643984" />
                                    <span class="lbexIndentClause">“(ii) the consequences of noncompliance with such requirement; and</span>

                                    <a id="HA7B33CB68D154138A78499E6F2E01B5F" />
                                    <span class="lbexIndentClause">“(iii) how to report to the State any change in the individual’s status that could result in—
                                        <a id="HB09BE6CAEBBF4AE59E4A9D5E8F63FB2B" />
                                        <span class="lbexIndentSubclause">“(I) the applicability of an exception under <a href="#HB95A875567A74FBC9933837B304F0F9C">paragraph (3)</a> (or the end of the applicability of such an exception); or</span>
                                        <a id="H2CBF9FA09AF44940A17C61A3152016EB" />
                                        <span class="lbexIndentSubclause">“(II) the individual qualifying as a specified excluded individual under <a href="#H5FDC36B12F4B4549AF8155AF1BCC1523">paragraph (9)(A)(ii)</a>.</span>
                                    </span>
                                </span>

                                <a id="HBBF098061F324BEE85F651A337DAFC73" />
                                <span class="lbexIndentSubpar">“(B) FORM OF OUTREACH NOTICE.—A notice required under <a href="#HC4EBE7D0D4884A48A3E91528D51709B3">subparagraph (A)</a> shall be delivered—
                                    <a id="HD8AC44B174144CE794CD234A9942FBBC" />
                                    <span class="lbexIndentClause">“(i) by regular mail (or, if elected by the individual, in an electronic format); and</span>
                                    <a id="H1ED3E4BC60304D998EBCEA50FB400DF2" />
                                    <span class="lbexIndentClause">“(ii) in 1 or more additional forms, which may include telephone, text message, an internet website, other commonly available electronic means, and such other forms as the Secretary determines appropriate.</span>
                                </span>
                            </span>

                            <a id="HD1FC5FB1B8864C1D93AF9A13166EF074" />
                            <span class="lbexIndentParagraph">“(9) DEFINITIONS.—In this subsection:

                                <a id="HC4EBE7D0D4884A48A3E91528D51709B3" />
                                <span class="lbexIndentSubpar">“(A) APPLICABLE INDIVIDUAL.—

                                    <a id="H172DAD532FFE4D74A65BA01D98AD9468" />
                                    <span class="lbexIndentClause">“(i) IN GENERAL.—The term ‘applicable individual’ means an individual (other than a specified excluded individual (as defined in <a href="#H5FDC36B12F4B4549AF8155AF1BCC1523">clause (ii)</a>))—
                                        <a id="HFA0D8C62FA4A4FBCAC1C636B8FA0F5E9" />
                                        <span class="lbexIndentSubclause">“(I) who is eligible to enroll (or is enrolled) under the State plan under subsection (a)(10)(A)(i)(VIII); or</span>
                                        <a id="H394852FECE82441C858299F422512C5D" />
                                        <span class="lbexIndentSubclause">“(II) who—
                                            <a id="H6DA32B725062462FB83E1B64F8AA3B6A" />
                                            <span class="lbexIndentItem">“(aa) is otherwise eligible to enroll (or is enrolled) under a waiver of such plan that provides coverage that is equivalent to minimum essential coverage (as described in <a
                                                href="https://uscode.house.gov/quicksearch/get.plx?title=26&amp;section=5000A"
                                                class="external"
                                                target="_blank"
                                            >section 5000A(f)(1)(A)</a> of the Internal Revenue Code of 1986 and as determined in accordance with standards prescribed by the Secretary in regulations); and</span>
                                            <a id="H0AB05EB87B934F82830CD629F93DAAD6" />
                                            <span class="lbexIndentItem">“(bb) has attained the age of 19 and is under 65 years of age, is not pregnant, is not entitled to, or enrolled for, benefits under part A of title XVIII, or enrolled for benefits under part B of title XVIII, and is not otherwise eligible to enroll under such plan.</span>

                                        </span>
                                    </span>

                                    <a id="H5FDC36B12F4B4549AF8155AF1BCC1523" />
                                    <span class="lbexIndentClause">“(ii) SPECIFIED EXCLUDED INDIVIDUAL.—For purposes of <a href="#H172DAD532FFE4D74A65BA01D98AD9468">clause (i)</a>, the term ‘specified excluded individual’ means an individual, as determined by the State (in accordance with standards specified by the Secretary)—
                                        <a id="HF21723377CA24D9CBEE6B8A961CA6CAF" />
                                        <span class="lbexIndentSubclause">“(I) who is described in subsection (a)(10)(A)(i)(IX);</span>
                                        <a id="HB116A11CEFBD432987C9AF7AB70F4868" />
                                        <span class="lbexIndentSubclause">“(II) who—
                                            <a id="H6DAB1873D3544D1E9A76CC18B93B64E1" />
                                            <span class="lbexIndentItem">“(aa) is an Indian or an Urban Indian (as such terms are defined in paragraphs (13) and (28) of section 4 of the Indian Health Care Improvement Act);</span>
                                            <a id="H6F74AF8ECABE4C43B2FFC8B8363C1865" />
                                            <span class="lbexIndentItem">“(bb) is a California Indian described in section 809(a) of such Act; or</span>

                                            <a id="HE48D11B2247144BC94DDF7F8A3AC0B9D" />
                                            <span class="lbexIndentItem">“(cc) has otherwise been determined eligible as an Indian for the Indian Health Service under regulations promulgated by the Secretary;</span>
                                        </span>

                                        <a id="H2F843E2A62A84FF88FDAB08323DCA7D9" />
                                        <span class="lbexIndentSubclause">“(III) who is the parent, guardian, caretaker relative, or family caregiver (as defined in section 2 of the RAISE Family Caregivers Act) of a dependent child 13 years of age and under or a disabled individual;</span>

                                        <a id="H90CFA312EEC74DD48C4F33218C91F09E" />
                                        <span class="lbexIndentSubclause">“(IV) who is a veteran with a disability rated as total under section 1155 of title 38, United States Code;</span>

                                        <a id="H149243134FB94F15A7B4C6B21FCD9BF9" />
                                        <span class="lbexIndentSubclause">“(V) who is medically frail or otherwise has special medical needs (as defined by the Secretary), including an individual—
                                            <a id="H290165ED719D4C6D9B5B62427A832526" />
                                            <span class="lbexIndentItem">“(aa) who is blind or disabled (as defined in section 1614);</span>
                                            <a id="H58557C14E7CE40A09B47146E028330EF" />
                                            <span class="lbexIndentItem">“(bb) with a substance use disorder;</span>

                                            <a id="H37732312F6EC4B79B73442DB73F0C990" />
                                            <span class="lbexIndentItem">“(cc) with a disabling mental disorder;</span>

                                            <a id="H2E86BEFFA06B438DB0E102341EF0C25B" />
                                            <span class="lbexIndentItem">“(dd) with a physical, intellectual or developmental disability that significantly impairs their ability to perform 1 or more activities of daily living; or</span>

                                            <a id="H6E04A802E039438E97833BAA01AB26EF" />
                                            <span class="lbexIndentItem">“(ee) with a serious or complex medical condition; </span>
                                        </span>

                                        <a id="HD53DC90E299F440C9831D34388EFC952" />
                                        <span class="lbexIndentSubclause">“(VI) who—
                                            <a id="H22357B7220944A71AF87D8ECF5B3CF21" />
                                            <span class="lbexIndentItem">“(aa) is in compliance with any requirements imposed by the State pursuant to section 407; or</span>
                                            <a id="H499CFB91ED82427F9F787D17F56E491E" />
                                            <span class="lbexIndentItem">“(bb) is a member of a household that receives supplemental nutrition assistance program benefits under the Food and Nutrition Act of 2008 and is not exempt from a work requirement under such Act;</span>
                                        </span>

                                        <a id="H2A46942930D44C13BA8900884CE1F281" />
                                        <span class="lbexIndentSubclause">“(VII) who is participating in a drug addiction or alcoholic treatment and rehabilitation program (as defined in section 3(h) of the Food and Nutrition Act of 2008);</span>

                                        <a id="H3B7727DEE5824A83BF0FA392899C8A9A" />
                                        <span class="lbexIndentSubclause">“(VIII) who is an inmate of a public institution; or</span>

                                        <a id="H7B6001B7B46D403D86FA46BD599141C4" />
                                        <span class="lbexIndentSubclause">“(IX) who is pregnant or entitled to postpartum medical assistance under paragraph (5) or (16) of subsection (e).</span>
                                    </span>
                                </span>

                                <a id="H38FE2E8F7DD94D7BA06EEE91F35B459C" />
                                <span class="lbexIndentSubpar">“(B) EDUCATIONAL PROGRAM.—The term ‘educational program’ includes—
                                    <a id="HE9F3C648147D4ED896E90E7C8D45CB90" />
                                    <span class="lbexIndentClause">“(i) an institution of higher education (as defined in section 101 of the Higher Education Act of 1965); and</span>
                                    <a id="HE15A562551BF4132A6847DC10E5DDED0" />
                                    <span class="lbexIndentClause">“(ii) a program of career and technical education (as defined in section 3 of the Carl D. Perkins Career and Technical Education Act of 2006).</span>
                                </span>

                                <a id="H67B1B60D41524DF1BCA4C9753F3DF577" />
                                <span class="lbexIndentSubpar">“(C) STATE.—The term ‘State’ means 1 of the 50 States or the District of Columbia.</span>

                                <a id="HF7FD55813CAF4E7B9D256817CF36DA8A" />
                                <span class="lbexIndentSubpar">“(D) WORK PROGRAM.—The term ‘work program’ has the meaning given such term in section 6(o)(1) of the Food and Nutrition Act of 2008.</span>

                            </span>

                            <a id="H9AEBFD708428401D9C1F3A029C1DF2CF" />
                            <span class="lbexIndentParagraph">“(10) PROHIBITING WAIVER OF COMMUNITY ENGAGEMENT REQUIREMENTS.—Notwithstanding section 1115(a), the provisions of this subsection may not be waived.</span>

                            <a id="H7D902FD6E393441BBBC8B4F14F38CD88" />
                            <span class="lbexIndentParagraph">“(11) SPECIAL IMPLEMENTATION RULE.—

                                <a id="H8C8D7FE3DDC042E59574DE5A1453F729" />
                                <span class="lbexIndentSubpar">“(A) IN GENERAL.—Subject to subparagraph (C), the Secretary may exempt a State from compliance with the requirements of this subsection if—
                                    <a id="H1DE1C6F5B18F4570BEAE61641F0AF126" />
                                    <span class="lbexIndentClause">“(i) the State submits to the Secretary a request for such exemption, made in such form and at such time as the Secretary may require, and including the information specified in subparagraph (B); and</span>
                                    <a id="HA37428FBEAD9495AB73F8A980C020302" />
                                    <span class="lbexIndentClause">“(ii) the Secretary determines that based on such request, the State is demonstrating a good faith effort to comply with the requirements of this subsection.</span>
                                </span>

                                <a id="H5480A10955824BC38F396181C0340DF2" />
                                <span class="lbexIndentSubpar">“(B) GOOD FAITH EFFORT DETERMINATION.—In determining whether a State is demonstrating a good faith effort for purposes of subparagraph (A)(ii), the Secretary shall consider—
                                    <a id="HC25EE266BD394AF7BE68A1DC0BADEB81" />
                                    <span class="lbexIndentClause">“(i) any actions taken by the State toward compliance with the requirements of this subsection;</span>
                                    <a id="HAF62965192CC4A1496328D6A96A337E4" />
                                    <span class="lbexIndentClause">“(ii) any significant barriers to or challenges in meeting such requirements, including related to funding, design, development, procurement, or installation of necessary systems or resources;</span>

                                    <a id="H1ECFD9BC2B8F47D6AD3D3E67DA288B8D" />
                                    <span class="lbexIndentClause">“(iii) the State's detailed plan and timeline for achieving full compliance with such requirements, including any milestones of such plan (as defined by the Secretary); and</span>

                                    <a id="HCC7C1C2A1B604C199A46FAC505EFD590" />
                                    <span class="lbexIndentClause">“(iv) any other criteria determined appropriate by the Secretary.</span>

                                </span>

                                <a id="HF32E0CFA656E4B8482602EE5F7D8D3A4" />
                                <span class="lbexIndentSubpar">“(C) DURATION OF EXEMPTION.—
                                    <a id="H5BCC9CBCEA864132B98ABB94729D06DD" />
                                    <span class="lbexIndentClause">“(i) IN GENERAL.—An exemption granted under subparagraph (A) shall expire not later than December 31, 2028, and may not be renewed beyond such date.</span>
                                    <a id="HFCA7D6E1ACB6469F9B6B5E5C284DA8D4" />
                                    <span class="lbexIndentClause">“(ii) EARLY TERMINATION.—The Secretary may terminate an exemption granted under subparagraph (A) prior to the expiration date of such exemption if the Secretary determined that the State has—
                                        <a id="HC0854E3308404F96BFDE6F243607B603" />
                                        <span class="lbexIndentSubclause">“(I) failed to comply with the reporting requirements described in subparagraph (D); or</span>
                                        <a id="HCD68E2C7730D4C4684475CFCFAF7691C" />
                                        <span class="lbexIndentSubclause">“(II) based on the information provided pursuant to subparagraph (D), failed to make continued good faith efforts toward compliance with the requirements of this subsection.</span>
                                    </span>
                                </span>

                                <a id="H4F6AEABD209A4911AA7CC895F82F9EA9" />
                                <span class="lbexIndentSubpar">“(D) REPORTING REQUIREMENTS.—A State granted an exemption under subparagraph (A) shall submit to the Secretary—
                                    <a id="H5D032198DB4A4D3794FEB215043C767D" />
                                    <span class="lbexIndentClause">“(i) quarterly progress reports on the State's status in achieving the milestones toward full compliance described in subparagraph (B)(iii); and</span>
                                    <a id="HFB4D117F849D48859AA65232664BBCAD" />
                                    <span class="lbexIndentClause">“(ii) information on specific risks or newly identified barriers or challenges to full compliance, including the State's plan to mitigate such risks, barriers, or challenges.”.</span>
                                </span>
                            </span>
                        </span>
                    </span>
                </span>

                <a id="HD73A0A07C3EF48EE94CB56DC583A01D2" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">Conforming amendment</span>.—Section 1902(a)(10)(A)(i)(VIII) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396a&num=0&edition=prelim#substructure-location_a_10_A_i_VIII"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396a(a)(10)(A)(i)(VIII)</a>) is amended by striking “subject to subsection (k)” and inserting <span class="annotated-text">“subject to subsections (k) and (xx)”</span>.</span>
                <a id="H214E8D10AFF84B56BA50969CE3326973" />
                <span class="lbexIndent">(c)
                    <span class="lbexSectionLevelOLCnuclear">Prohibiting conflicts of interest</span>.—A State shall not use a Medicaid managed care entity or other specified entity (as such terms are defined in section 1903(m)(9)(D)), or other contractor to determine beneficiary compliance under such section unless the contractor has no direct or indirect financial relationship with any Medicaid managed care entity or other specified entity that is responsible for providing or arranging for coverage of medical assistance for individuals enrolled with the entity pursuant to a contract with such State.</span>
                <a id="HDBD1E781D46C447684F40DF1329A0718" />
                <span class="lbexIndent">(d)
                    <span class="lbexSectionLevelOLCnuclear">Interim final rulemaking</span>.—Not later than June 1, 2026, the Secretary of Health and Human Services shall promulgate an interim final rule for purposes of implementing the provisions of, and the amendments made by, this section. Any action taken to implement the provisions of, and the amendments made by, this section shall not be subject to the provisions of section 553 of title 5, United States Code.</span>
                <a id="H85F477A2145F48D69A1C27294699ACE9" />
                <span class="lbexIndent">(e)
                    <span class="lbexSectionLevelOLCnuclear">Development of government efficiency grants to States</span>.—
                    <a id="HCD4D39ECB4B74882B4AB4EEFE97773C6" />
                    <span class="lbexIndentParagraph">(1) IN GENERAL.—In order for States to establish systems necessary to carry out the provisions of, and amendments made by, this section or other sections of this chapter that pertain to conducting eligibility determinations or redeterminations, the Secretary of Health and Human Services shall—
                        <a id="H1B5F4DDDD23E44A1BE4A2DBBFC791B1B" />
                        <span class="lbexIndentSubpar">(A) out of amounts appropriated under paragraph (3)(A), award to each State a grant equal to the amount specified in paragraph (2) for such State; and</span>
                        <a id="HF51FEA7992154986B4591BC838B517AD" />
                        <span class="lbexIndentSubpar">(B) out of amounts appropriated under paragraph (3)(B), distribute an equal amount among such States.</span>
                    </span>

                    <a id="H5A642250EBC6404480900C98CC529A90" />
                    <span class="lbexIndentParagraph">(2) AMOUNT SPECIFIED.—For purposes of paragraph (1)(A), the amount specified in this paragraph is an amount that bears the same ratio to the amount appropriated under paragraph (3)(A) as the number of applicable individuals (as defined in section 1902(xx) of the Social Security Act, as added by subsection (a)) residing in such State bears to the total number of such individuals residing in all States, as of March 31, 2025.</span>

                    <a id="H585005018A214F2DBD75AA8E5D24BB2F" />
                    <span class="lbexIndentParagraph">(3) FUNDING.—There are appropriated, out of any monies in the Treasury not otherwise appropriated—
                        <a id="H018E6247C1CE4722B632C1665113B312" />
                        <span class="lbexIndentSubpar">(A) $100,000,000 for fiscal year 2026 for purposes of awarding grants under paragraph (1)(A), to remain available until expended; and</span>
                        <a id="HF7EFF78604E84FD6AE3D052E668BFFA8" />
                        <span class="lbexIndentSubpar">(B) $100,000,000 for fiscal year 2026 for purposes of award grants under paragraph (1)(B), to remain available until expended.</span>
                    </span>

                    <a id="HBD381FB3BCD4467BAA8BCA4B9B122999" />
                    <span class="lbexIndentParagraph">(4) DEFINITION.—In this subsection, the term “State” means 1 of the 50 States and the District of Columbia. </span>
                </span>

                <a id="H9EE2B570A2054FDF9EB5FD358672F37E" />
                <span class="lbexIndent">(f)
                    <span class="lbexSectionLevelOLCnuclear">Implementation funding</span>.—For the purposes of carrying out the provisions of, and the amendments made by, this section, there are appropriated, out of any monies in the Treasury not otherwise appropriated, to the Administrator of the Centers for Medicare &amp; Medicaid Services, $200,000,000 for fiscal year 2026, to remain available until expended.</span>

                <span class="lbexHang">
                    <a id="toc-H4ADCA385302C45CCBDC2C4550A5A6759" href="#H4ADCA385302C45CCBDC2C4550A5A6759">
                        <span class="lbexHangWithMargin">
                            <span id="H4ADCA385302C45CCBDC2C4550A5A6759" />
                            <span class="lbexSectionlevelOLC">Sec. 71120. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Modifying cost sharing requirements for certain expansion individuals under the Medicaid program</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="HD8C2EFE59E624828BEE359C477862C45" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">In general</span>.—Section 1916 of the Social Security Act (<a
                        href="https://uscode.house.gov/quicksearch/get.plx?title=42&amp;section=1396o"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396o</a>) is amended—
                    <a id="HD014FD8F280B45ED9B0BD903AD086525" />
                    <span class="lbexIndentParagraph">(1) in subsection (a), in the matter preceding paragraph (1), by inserting <span class="annotated-text">“(other than, beginning October 1, 2028, specified individuals (as defined in subsection (k)(3)))”</span> after “individuals”; and</span>
                </span>
                <a id="HA206E2E795374C2D9179A8C9AE42F25F" />
                <span class="lbexIndentParagraph">
                    <span class="lbexIndent">(2) by adding at the end the following new subsection:
                        <span class="lbexIndentSubsection">
                            <a id="H42BBFD5AD4B54589BC40ACA1CADC715F" />
                            <span class="lbexIndentSubsection">
                                <span class="lbexIndent">“(k)
                                    <span class="lbexSectionLevelOLCnuclear">Special rules for certain expansion individuals</span>.—
                                    <a id="HACC5674CC55745438EDE634E71B170AC" />
                                    <span class="lbexIndentParagraph">“(1) PREMIUMS.—Beginning October 1, 2028, the State plan shall provide that in the case of a specified individual (as defined in paragraph (3)) who is eligible under the plan, no enrollment fee, premium, or similar charge will be imposed under the plan.</span>
                                </span>
                                <a id="H2032156D6D764FE689D0CC815F9753F5" />
                                <span class="lbexIndentParagraph">“(2) REQUIRED IMPOSITION OF COST SHARING.—
                                    <a id="HAA58CE7AE17A4E0CA5E123B5CAF77DA5" />
                                    <span class="lbexIndentSubpar">“(A) IN GENERAL.—Subject to subparagraph (B) and subsection (j), in the case of a specified individual, the State plan shall, beginning October 1, 2028, provide for the imposition of such deductions, cost sharing, or similar charges determined appropriate by the State (in an amount greater than $0) with respect to certain care, items, or services furnished to such an individual, as determined by the State.</span>
                                    <a id="H1760FE922B784A9CB61C2AF4D6E40679" />
                                    <span class="lbexIndentSubpar">“(B) LIMITATIONS.—
                                        <a id="HF15E355164554DE599911EB91E57B310" />
                                        <span class="lbexIndentClause">“(i) EXCLUSION OF CERTAIN SERVICES.—In no case may a deduction, cost sharing, or similar charge be imposed under the State plan with respect to care, items, or services described in any of subparagraphs (B) through (J) of subsection (a)(2), or any primary care services, mental health care services, substance use disorder services, or services provided by a Federally qualified health center (as defined in 1905(l)(2)), certified community behavioral health clinic (as defined in section 1905(jj)(2)), or rural health clinic (as defined in 1905(l)(1)), furnished to a specified individual.</span>
                                        <a id="H951689DACC0C4034929314ADF4DF981F" />
                                        <span class="lbexIndentClause">“(ii) ITEM AND SERVICE LIMITATION.—
                                            <a id="H80370273AE4C4E099B54DCC7D2CA8721" />
                                            <span class="lbexIndentSubclause">“(I) IN GENERAL.—Except as provided in subclause (II), in no case may a deduction, cost sharing, or similar charge imposed under the State plan with respect to care or an item or service furnished to a specified individual exceed $35.</span>
                                            <a id="HE7C0B22D73BA46E9888F80D4CC75C03D" />
                                            <span class="lbexIndentSubclause">“(II) SPECIAL RULES FOR PRESCRIPTION DRUGS.—In no case may a deduction, cost sharing, or similar charge imposed under the State plan with respect to a prescription drug furnished to a specified individual exceed the limit that would be applicable under paragraph (2)(A)(i) or (2)(B) of section 1916A(c) with respect to such drug and individual if such drug so furnished were subject to cost sharing under such section.</span>
                                        </span>
                                        <a id="H651CF257248543EBA0CB694FC147A56D" />
                                        <span class="lbexIndentClause">“(iii) MAXIMUM LIMIT ON COST SHARING.—The total aggregate amount of deductions, cost sharing, or similar charges imposed under the State plan for all individuals in the family may not exceed 5 percent of the family income of the family involved, as applied on a quarterly or monthly basis (as specified by the State).</span>
                                    </span>
                                    <a id="H17CE0A4832B24FFEA553A9F4BE9A9AAE" />
                                    <span class="lbexIndentSubpar">“(C) CASES OF NONPAYMENT.—Notwithstanding subsection (e), a State may permit a provider participating under the State plan to require, as a condition for the provision of care, items, or services to a specified individual entitled to medical assistance under this title for such care, items, or services, the payment of any deductions, cost sharing, or similar charges authorized to be imposed with respect to such care, items, or services. Nothing in this subparagraph shall be construed as preventing a provider from reducing or waiving the application of such deductions, cost sharing, or similar charges on a case-by-case basis.</span>
                                </span>
                            </span>
                            <a id="HD6027B639CDB4F59B2E8071DBD8AA9D6" />
                            <span class="lbexIndentParagraph">“(3) SPECIFIED INDIVIDUAL DEFINED.—For purposes of this subsection, the term ‘specified individual’ means an individual who has a family income (as determined in accordance with section 1902(e)(14)) that exceeds the poverty line (as defined in section 2110(c)(5)) applicable to a family of the size involved and—
                                <a id="HA11A7B44D14E4554B38BFEAAF6CD5194" />
                                <span class="lbexIndentSubpar">“(A) is enrolled under section 1902(a)(10)(A)(i)(VIII); or</span>
                                <a id="HB5FBE619E4DD42D7B7EE7E5F949F42EF" />
                                <span class="lbexIndentSubpar">“(B) is described in such subsection and otherwise enrolled under a waiver of the State plan that provides coverage that is equivalent to minimum essential coverage (as described in <a
                                    href="https://uscode.house.gov/quicksearch/get.plx?title=26&amp;section=5000A"
                                    class="external"
                                    target="_blank"
                                >section 5000A(f)(1)(A)</a> of the Internal Revenue Code of 1986 and determined in accordance with standards prescribed by the Secretary in regulations) to all individuals described in section 1902(a)(10)(A)(i)(VIII).</span>
                            </span>
                            <a id="HA50450ED039C4BD8A627283D1FCBBEEC" />
                            <span class="lbexIndentParagraph">“(4) STATE DEFINED.—For purposes of this subsection, the term ‘State’ means 1 of the 50 States or the District of Columbia.”.</span>
                        </span>
                    </span>
                </span>

                <a id="H831A10105D3A4B6A917790ECD97197FF" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">Conforming amendments</span>.—
                    <a id="H09151CE0186646DC87BE91BBFE5EE99F" />
                    <span class="lbexIndentParagraph">(1) REQUIRED APPLICATION.—Section 1902(a)(14) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396a&num=0&edition=prelim#substructure-location_a_14"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396a(a)(14)</a>) is amended by inserting <span class="annotated-text">“and provide for imposition of such deductions, cost sharing, or similar charges for care, items, or services furnished to specified individuals (as defined in paragraph (3) of section 1916(k)) in accordance with paragraph (2) of such section”</span> after “section 1916”.</span>
                </span>
                <a id="H13A29E0011FC45E9819A7CF3D0D061EF" />
                <span class="lbexIndentParagraph">(2) NONAPPLICABILITY OF ALTERNATIVE COST SHARING.—Section 1916A(a)(1) of the Social Security Act (<a
                    href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396o-1&num=0&edition=prelim#substructure-location_a_1"
                    class="external"
                    target="_blank"
                >42 U.S.C. 1396o–1(a)(1)</a>) is amended, in the second sentence, by striking “or (j)” and inserting <span class="annotated-text">“(j), or (k)”</span>.</span>

                <a id="H955C2E1C379E470A8E2C7F3DF31D1EB0" />
                <span class="lbexIndent">(c)
                    <span class="lbexSectionLevelOLCnuclear">Implementation funding</span>.—For the purposes of carrying out the provisions of, and the amendments made by, this section, there are appropriated, out of any monies in the Treasury not otherwise appropriated, to the Administrator of the Centers for Medicare &amp; Medicaid Services, $15,000,000 for fiscal year 2026, to remain available until expended.</span>
                <a id="H2388F94754554D3C9E54A32152DEE520" />

                <a id="toc-H2388F94754554D3C9E54A32152DEE520" href="#H2388F94754554D3C9E54A32152DEE520">
                    <span class="lbexSubChapterLevelOLC">Subchapter E — Expanding Access to Care</span>
                </a>

                <span class="lbexHang">
                    <a id="toc-H09652BCC85234E4FAAAC9D9A805494AF" href="#H09652BCC85234E4FAAAC9D9A805494AF">
                        <span class="lbexHangWithMargin">
                            <span id="H09652BCC85234E4FAAAC9D9A805494AF" />
                            <span class="lbexSectionlevelOLC">Sec. 71121. </span>
                            <span class="lbexSectionlevelOLC">
                                <span class="lbexAllcap">Making certain adjustments to coverage of home or community-based services under Medicaid</span>.
                            </span>
                        </span>
                    </a>
                </span>

                <a id="H8F4E00E92C574C8D98E1F0E93E875667" />
                <span class="lbexIndent">(a)
                    <span class="lbexSectionLevelOLCnuclear">Expanding HCBS coverage under section 1915(c) waivers</span>.—Section 1915(c) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396n&num=0&edition=prelim#substructure-location_c"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396n(c)</a>) is amended—
                    <a id="H46B8515A24A24C50B92600B7B6C49E37" />
                    <span class="lbexIndentParagraph">(1) in paragraph (3), by inserting <span class="annotated-text">“paragraph (11) or”</span> before “subsection (h)(2)”; and</span>

                    <a id="HBED303E2D313405B8959D63E1A4BB49D" />
                    <span class="lbexIndentParagraph">(2) by adding at the end the following new paragraph:
                        <span class="lbexIndentSubsection">
                            <a id="H90CD96A9792646019CB5122BA4FE76E1" />
                            <span class="lbexIndentParagraph">“(11)
                                <span class="lbexSectionTitleTrad">Expanding coverage for home or community-based services</span>.—
                                <a id="H2227FAB9D9F64250A45B7F89F3617F73" />
                                <span class="lbexIndentParagraph">“(A) IN GENERAL.—Beginning July 1, 2028, notwithstanding paragraph (1), the Secretary may approve a waiver that is standalone from any other waiver approved under this subsection to include as medical assistance under the State plan of such State payment for part or all of the cost of home or community-based services (other than room and board (as described in paragraph (1))) approved by the Secretary which are provided pursuant to a written plan of care to individuals described in subparagraph (B)(iii). A waiver approved under this paragraph shall be for an initial term of 3 years and, upon the request of the State, shall be extended for additional 5-year periods unless the Secretary determines that for the previous waiver period the requirements specified under this subsection (excluding those excepted under subparagraph (B)) have not been met.</span>
                            </span>
                            <a id="HF0FC508997F844618B2EE75E0964EF57" />
                            <span class="lbexIndentParagraph">“(B) STATE REQUIREMENTS.—In addition to the requirements specified under this subsection (except for the requirements described in subparagraphs (C) and (D) of paragraph (2) and any other requirement specified under this subsection that the Secretary determines to be inapplicable in the context of a waiver that does not require individuals to have a determination described in paragraph (1)), a State shall meet the following requirements as a condition of waiver approval:
                                <a id="HEF0912F032314BD4AC4FD58367CEA229" />
                                <span class="lbexIndentSubpar">“(i) As of the date that such State requests a waiver under this subsection to provide home or community-based services to individuals described in clause (iii), all other waivers (if any) granted under this subsection to such State meet the requirements of this subsection.</span>
                                <a id="H5F7963A6D3AF40F28F286AFCFAE8626B" />
                                <span class="lbexIndentSubpar">“(ii) The State demonstrates to the Secretary that approval of a waiver under this subsection with respect to individuals described in clause (iii) will not result in a material increase of the average amount of time that individuals with respect to whom a determination described in paragraph (1) has been made will need to wait to receive home or community-based services under any other waiver granted under this subsection, as determined by the Secretary.</span>
                                <a id="H2FB92DA73A60468EB105D160634EBAFB" />
                                <span class="lbexIndentSubpar">“(iii) The State establishes needs-based criteria, subject to the approval of the Secretary, regarding who will be eligible for home or community-based services under a waiver approved under this paragraph without requiring such individuals to have a determination described in paragraph (1), and specifies the home or community-based services such individuals so eligible will receive.</span>
                                <a id="H2616B1B99DE6496284CB50C713B99DB1" />
                                <span class="lbexIndentSubpar">“(iv) The State establishes needs-based criteria for determining whether an individual described in clause (iii) requires the level of care provided in a hospital, nursing facility, or an intermediate care facility for individuals with developmental disabilities under the State plan or under any waiver of such plan that are more stringent than the needs-based criteria established under clause (iii) for determining eligibility for home or community-based services.</span>

                                <a id="H4205859E3C184896AAA33B5EEC24BB65" />
                                <span class="lbexIndentSubpar">“(v) The State attests that the State’s average per capita expenditure for medical assistance under the State plan (or waiver of such plan) provided with respect to such individuals enrolled in a waiver under this paragraph will not exceed the State’s average per capita expenditure for medical assistance for individuals receiving institutional care under the State plan (or waiver of such plan) for the duration that the waiver under this paragraph is in effect.</span>

                                <a id="H11C1AEC6C60E46B59482318AD8313EB4" />
                                <span class="lbexIndentSubpar">“(vi) The State provides to the Secretary data (in such form and manner as the Secretary may specify) regarding the number of individuals described in clause (iii) with respect to a State seeking approval of a waiver under this subsection, to whom the State will make such services available under such waiver.</span>

                                <a id="H357D33BA21984FE1AB843799A3A6324B" />
                                <span class="lbexIndentSubpar">“(vii) The State agrees to provide to the Secretary, not less frequently than annually, data for purposes of paragraph (2)(E) (in such form and manner as the Secretary may specify) regarding, with respect to each preceding year in which a waiver under this subsection to provide home or community-based services to individuals described in clause (iii) was in effect—
                                    <a id="H051739D6865D4786A795872BD2062BA0" />
                                    <span class="lbexIndentClause">“(I) the cost (as such term is defined by the Secretary) of such services furnished to individuals described in clause (iii), broken down by type of service;</span>
                                    <a id="HD86C4524B5A24D8CA3A3A29E55142494" />
                                    <span class="lbexIndentClause">“(II) with respect to each type of home or community-based service provided under the waiver, the length of time that such individuals have received such service;</span>

                                    <a id="H0F9F13CC9EB54022B3E7C30CDC8398C8" />
                                    <span class="lbexIndentClause">“(III) a comparison between the data described in subclause (I) and any comparable data available with respect to individuals with respect to whom a determination described in paragraph (1) has been made and with respect to individuals receiving institutional care under this title; and</span>

                                    <a id="H3A05A36F3D304D5C839298A5974E0441" />
                                    <span class="lbexIndentClause">“(IV) the number of individuals who have received home or community-based services under the waiver during the preceding year.</span>
                                </span>
                            </span>

                            <a id="HB2D6E9C2A73647078D00CFBAB80B0738" />
                            <span class="lbexIndentParagraph">“(C) LIMITATION ON PAYMENTS.—No payments made to carry out this paragraph shall be used by a State to make payments to a third party on behalf of an individual practitioner for benefits such as health insurance, skills training, and other benefits customary for employees, in the case of a class of practitioners for which the program established under this title is the primary source of revenue.”.</span>
                        </span>
                    </span>
                </span>

                <a id="H767CFA36946B47ACBB4C9703EB97EE6D" />
                <span class="lbexIndent">(b)
                    <span class="lbexSectionLevelOLCnuclear">Implementation funding</span>.—
                    <a id="HC0B1F20E7ABB4EAA9AE772030EE4B9BA" />
                    <span class="lbexIndentParagraph">(1) IN GENERAL.—There are appropriated, out of any monies in the Treasury not otherwise appropriated, to the Administrator of the Centers for Medicare &amp; Medicaid Services—
                        <a id="HD5B41E2356F2469489B0B7CD8CB79958" />
                        <span class="lbexIndentSubpar">(A) for fiscal year 2026, $50,000,000 for purposes of carrying out the provisions of, and the amendments made by, this section, to remain available until expended; and</span>

                        <a id="H00AE6B0E31E3445183E405CA6E007DB5" />
                        <span class="lbexIndentSubpar">(B) for fiscal year 2027, $100,000,000 for purposes of making payments to States, subject to paragraph (2), to support State systems to deliver home or community-based services under section 1915(c) of the Social Security Act (<a
                            href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396n&num=0&edition=prelim#substructure-location_c"
                            class="external"
                            target="_blank"
                        >42 U.S.C. 1396n(c)</a>) (as amended by this section) or under section 1115 of such Act (<a
                            href="https://uscode.house.gov/quicksearch/get.plx?title=42&amp;section=1315"
                            class="external"
                            target="_blank"
                        >42 U.S.C. 1315</a>), to remain available until expended.</span>
                    </span>

                    <a id="H049F6580A824403F9ACCBED4B8F41ED5" />
                    <span class="lbexIndentParagraph">(2) PAYMENTS BASED ON STATE HCBS ELIGIBLE POPULATION.—Payments to States from amounts made available by paragraph (1)(B) shall be made, with respect to a State, on the basis of the proportion of the population of the State that is receiving home or community-based services under section1915(c) of the Social Security Act (<a
                        href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396n&num=0&edition=prelim#substructure-location_c"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1396n(c)</a>) (as amended by this section) or under section 1115 of such Act (<a
                        href="https://uscode.house.gov/quicksearch/get.plx?title=42&amp;section=1315"
                        class="external"
                        target="_blank"
                    >42 U.S.C. 1315</a>), as compared to all States. </span>
                </span>
            </div>
        </div>
    </div>
</template>

<style scoped>
.lbexTocSectionOLC {
display: block;
margin-top: 1em;
margin-bottom: 1em;
}
.lbexTocSubChapterOLC, .lbexTocSubTitleOLC {
font-size: 110%;
font-weight: bold;
display: block;
margin-top: 1em;
margin-bottom: 1em;
}
.lbexTocDivisionOLC {
font-size: 120%;
font-weight: bold;
display: block;
margin-top: 1em;
margin-bottom: 1em;
}
.lbexSubChapterLevelOLC, .lbexSubTitleLevelOLC, .lbexChapterLevelOLC {
display: block;
margin-top: 1em;
margin-bottom: 1em;
font-size: 150%;
font-weight: bold;
}
.lbexHang {
font-size: 120%;
font-weight: bold;
display: block;
margin-top: 1em;
margin-bottom: 1em;
}
.lbexIndent {
display: block;
margin-top: 1em;
margin-bottom: 1em;
/*margin-left: 1em;
padding-left: 5px;
border-left: 1px solid #d0d0d0;*/
}
.lbexIndentParagraph {
display: block;
margin-top: 1em;
margin-bottom: 1em;
margin-left: 0em;
padding-left: 2em;
border-left:  1px solid #d0d0d0;
}
.lbexIndentSectionText {
display: block;
margin-top: 1em;
margin-bottom: 1em;
}
.lbexIndentSubpar {
display: block;
margin-top: 1em;
margin-bottom: 1em;
margin-left: 0em;
padding-left: 2em;
border-left: 1px solid #d0d0d0;
}
.lbexIndentClause {
display: block;
margin-top: 1em;
margin-bottom: 1em;
margin-left: 0em;
padding-left: 2em;
border-left: 1px solid #d0d0d0;
}
.lbexIndentSubclause {
display: block;
margin-top: 1em;
margin-bottom: 1em;
margin-left: 0em;
padding-left: 2em;
border-left: 1px solid #d0d0d0;
}
.lbexIndentSubsection {
display: block;
background-color: #F2F2F2;
}
.annotated-text { background-color: #F2F2F2; }
.lbexIndentItem {
display: block;
margin-top: 1em;
margin-bottom: 1em;
margin-left: 0em;
padding-left: 2em;
border-left: 1px solid #d0d0d0;
}
.lbexIndentSubItem {
display: block;
margin-top: 1em;
margin-bottom: 1em;
margin-left: 0em;
padding-left: 2em;
border-left: 1px solid #d0d0d0;
}
.ul {
display: block;
margin-top: 1em;
margin-bottom: 1em;
}
a { text-decoration: none;}
.lbexSectionLevelOLCnuclear, .lbexSectionTitleTrad { font-weight: 700; }
</style>
