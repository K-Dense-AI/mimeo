# Frameworks of J. Brandon Dixon

Detailed steps and protocols developed by J. Brandon Dixon for biomechanical modeling, functional imaging, and preclinical testing.

## Non-Invasive Lymphatic Occlusion Pressure Measurement
In vivo diagnostic protocol using near-infrared fluorescent imaging and a dynamic occlusion cuff to quantify active pumping pressure and functional recovery.

### Protocol Steps:
1. **Tracer Administration**: Inject a small, non-perturbing volume of near-infrared fluorescent tracer (e.g., ICG conjugated to serum albumin or nanocarriers) intradermally in the distal tissue bed.
2. **Cuff Positioning**: Place a custom inflatable occlusion cuff downstream over the target collecting vessel.
3. **Complete Occlusion**: Inflate the cuff to a baseline pressure sufficient to collapse the vessel lumen completely, halting forward movement of fluorescent packets.
4. **Gradual Deflation**: Stepwise deflate cuff pressure while continuously recording dynamic near-infrared fluorescence at high frame rates.
5. **Threshold Identification**: Determine the exact pressure threshold at which active contractile packets overcome cuff resistance and resume downstream transport.
> "we inject a near-infrared tracer we see the lymphatic then we inflate this occlusion cuff right here to a level that completely um collapses the vessel and wait for the fluorescence to empty out then we gradually deflate the pressure in the cuff and then we can determine the pressure at which we see restoration of flow"
(sources: src_009, src_010)

## Longitudinal Volumetric and Functional Lymphedema Assessment
Preclinical protocol combining non-invasive 3D surface scanning with dynamic NIR imaging to track disease initiation, progression, and therapeutic responses over time.

### Protocol Steps:
1. **Clinically Relevant Injury**: Perform partial surgical node/vessel dissection or single-side vessel ligation combined with localized radiation, leaving intact alternative pathways.
2. **3D Surface Scanning**: Perform regular non-invasive 3D limb surface acquisition (e.g., handheld or mobile LiDAR scanning) to quantify volume changes and swelling percentage over baseline.
3. **Dynamic NIR Functional Imaging**: Quantify active pumping parameters—including contraction frequency, packet speed, stroke volume index, and occlusion pressure—at regular longitudinal timepoints.
4. **Histopathological Correlation**: Match long-term functional loss with tissue-level histopathology, evaluating epidermal thickness, collagen alignment, and subcutaneous fat expansion.
> "To characterize lymphatic alterations and their association with disease pathology in a clinically relevant model in the rat, we developed a longitudinal iPhone-based volumetry method combined with non-invasive NIR analysis of lymphatic function."
(sources: src_021)

## Lumped Parameter Mechanobiological Adaptation Framework
Computational framework modeling lymphangion fluid dynamics, active/passive wall mechanobiology, and structural growth laws under acute and chronic mechanical loads.

### Computational Steps:
1. **Lymphangion Fluid Dynamics**: Model individual lymphangion segments using lumped circuit parameters coupled with active smooth muscle contraction models and passive wall constitutive equations.
2. **Acute Vasoreactive Feedback**: Incorporate short-term feedback functions driven by fluid wall shear stress and transmural pressure to model acute vasomotion and tone adjustments.
3. **Chronic Structural Growth**: Implement constitutive growth laws driven by sustained wall hoop stress and pressure overload to calculate volumetric wall thickening, loss of elastic compliance, and eventual pump failure.
> "This theoretical framework combines a simplified version of a published lumped parameter model for lymphangion function and lymph transport, a published microstructurally motivated constitutive model for the active and passive mechanical behavior of isolated rat thoracic ducts, and novel models for acute mechanically mediated vasoreactive adaptations and long-term volumetric growth..."
(sources: src_018)
