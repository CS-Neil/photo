XMP_TEMPLATE = """<?xpacket begin='\xef\xbb\xbf' id='W5M0MpCehiHzreSzNTczkc9d'?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"
    crs:Version="15.4"
    crs:ProcessVersion="11.0"
    crs:WhiteBalance="Custom"
    crs:Temperature="{temperature}"
    crs:Tint="{tint}"
    crs:Exposure2012="{exposure}"
    crs:Contrast2012="{contrast}"
    crs:Highlights2012="{highlights}"
    crs:Shadows2012="{shadows}"
    crs:Whites2012="{whites}"
    crs:Blacks2012="{blacks}"
    crs:Vibrance="{vibrance}"
    crs:Saturation="{saturation}"
    crs:ToneCurveName2012="Custom"
    crs:SplitToningShadowHue="{split_shadow_hue}"
    crs:SplitToningShadowSaturation="{split_shadow_sat}"
    crs:SplitToningHighlightHue="{split_highlight_hue}"
    crs:SplitToningHighlightSaturation="{split_highlight_sat}"
    crs:SplitToningBalance="{split_balance}"
    crs:HasSettings="True">
   <crs:ToneCurvePV2012>
    <rdf:Seq>
     <rdf:li>0, 0</rdf:li>
     <rdf:li>{tc_shadows_x}, {tc_shadows_y}</rdf:li>
     <rdf:li>{tc_darks_x}, {tc_darks_y}</rdf:li>
     <rdf:li>{tc_lights_x}, {tc_lights_y}</rdf:li>
     <rdf:li>{tc_highlights_x}, {tc_highlights_y}</rdf:li>
     <rdf:li>255, 255</rdf:li>
    </rdf:Seq>
   </crs:ToneCurvePV2012>
   <crs:ToneCurvePV2012Red>
    <rdf:Seq>
     <rdf:li>0, 0</rdf:li>
     <rdf:li>255, 255</rdf:li>
    </rdf:Seq>
   </crs:ToneCurvePV2012Red>
   <crs:ToneCurvePV2012Green>
    <rdf:Seq>
     <rdf:li>0, 0</rdf:li>
     <rdf:li>255, 255</rdf:li>
    </rdf:Seq>
   </crs:ToneCurvePV2012Green>
   <crs:ToneCurvePV2012Blue>
    <rdf:Seq>
     <rdf:li>0, 0</rdf:li>
     <rdf:li>255, 255</rdf:li>
    </rdf:Seq>
   </crs:ToneCurvePV2012Blue>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end='w'?>"""


def generate_xmp(params: dict) -> str:
    """Generate an XMP preset file from Lightroom parameters."""
    basic = params["basic"]
    wb = params["white_balance"]
    presence = params["presence"]
    tc = params["tone_curve"]
    st = params["split_toning"]

    return XMP_TEMPLATE.format(
        temperature=wb["temperature"],
        tint=wb["tint"],
        exposure=basic["exposure"],
        contrast=basic["contrast"],
        highlights=basic["highlights"],
        shadows=basic["shadows"],
        whites=basic["whites"],
        blacks=basic["blacks"],
        vibrance=presence["vibrance"],
        saturation=presence["saturation"],
        split_shadow_hue=st["shadow_hue"],
        split_shadow_sat=st["shadow_saturation"],
        split_highlight_hue=st["highlight_hue"],
        split_highlight_sat=st["highlight_saturation"],
        split_balance=st["balance"],
        tc_shadows_x=tc["shadows"]["x"],
        tc_shadows_y=tc["shadows"]["y"],
        tc_darks_x=tc["darks"]["x"],
        tc_darks_y=tc["darks"]["y"],
        tc_lights_x=tc["lights"]["x"],
        tc_lights_y=tc["lights"]["y"],
        tc_highlights_x=tc["highlights"]["x"],
        tc_highlights_y=tc["highlights"]["y"],
    )
