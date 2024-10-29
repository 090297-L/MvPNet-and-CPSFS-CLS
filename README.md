# MvPNet-and-CPSFSC
Multi-view Perceptive Network for Few-Shot IC Package Substrates Surface Defect Classification: Benchmark Methodology and Dataset

## Data Link
The dataset is uploaded into Google Drive, and the source train and val set data can be download in [Google drive](https://drive.google.com/file/d/1fulLTcfHK7eb9ldH-M_pkF55djsDVT4Q/view?usp=drive_link).


## AOI System and Dataset

Initially, the CPS sample is positioned at the input port.     As it enters the system, the transmission mechanism uses a suction cup to transport the CPS to the data acquisition area.   Upon reaching the data acquisition area, a high-resolution camera captures images of the CPS sample.     The system employs window cropping techniques to refine the captured data, extracting a focused CPSFSC dataset.  Then, MvPNet is utilized for defect classification, effectively learning and identifying potential defects even with limited CPS data.     This capability provides a significant advantage in data-constrained scenarios.     The identified defects are presented through an interactive visual interface, enabling operators to view annotated defect regions and access expanded views.

<div align=center>
  
![AOI System](https://github.com/user-attachments/assets/1fc74352-7e16-4b54-951e-3eab93798b80)

</div>



## Data Description

The CPSFSC dataset comprises 18 types of ICPS with various defects, including 12 types of defective single-layer CPS and 6 assembled multi-layer CPS. We randomly divide these 18 types of CPS into a training set, validation set, and test set. The train set includes 6 types of single-layer CPS and 2 types of multi-layer data. Both the validation set and the test set consist of 3 types of single-layer CPS and 2 types of multi-layer CPS. The data in the train set, validation set, and test set are mutually exclusive, meaning that during testing, the model encounters only unseen data categories. This setup provides a more robust evaluation of the few-shot classification algorithm's performance.
<div align=center>
  
![Distribution in CPSFS-CLS](https://github.com/user-attachments/assets/e375741d-2afc-4173-927f-94ec523004b4) ![Proportion in CPSFS-CLS](https://github.com/user-attachments/assets/e42e3f4f-0fb4-4b37-a77d-ce80abdd1a55)

</div>

## Benchmark Methodology

MvPNet consists of three modules: the Perceptive Class-changed Interaction Module, responsible for feature aggregation perception during class changes; the Multi-view Position Aggregation Module, which observes the regions of interest from multiple views and ensures intra-class connectivity; and the Position Localization Refinement Module, which enhances positional information to ensure the stability of features from local to global scales.

![MvPNet](https://github.com/user-attachments/assets/a52652f6-2d7b-4fbc-8a7b-5ee1abd86a09)

## Experiments results

All comparison algorithms can be found in 

* [LibFewShot](https://github.com/rl-vig/libfewshot)
* [GTNet](https://github.com/VDT-2048/FSC-20)
* [FaNet](https://github.com/successhaha/GTnet)
* [Bi-FRN](https://github.com/PRIS-CV/Bi-FRN)
* [ESPT](https://github.com/Whut-YiRong/ESPT)
* [CPEA](https://github.com/FushengHao/CPEA)
* [AMMD](https://github.com/WuJi1/AMMD)

### [CPSFSC Dataset](https://drive.google.com/file/d/1fulLTcfHK7eb9ldH-M_pkF55djsDVT4Q/view?usp=drive_link)

<div align=center>

![Comparison With SOTA Algorithms in CPSFS-CLS](https://github.com/user-attachments/assets/df4d9835-b1c3-4965-9e1b-6829304237f6) ![CPS_keshihua](https://github.com/user-attachments/assets/d0d3729a-ce7d-406d-a43c-c340744dfcf8)

</div>

### [FSC-20 Dataset](https://github.com/VDT-2048/FSC-20)

<div align=center>

![Comparison With SOTA Algorithms in FSC-20](https://github.com/user-attachments/assets/4ac607c5-c002-4f87-af48-6a4795ffc446) ![FSC_keshihua](https://github.com/user-attachments/assets/f2a7bbf1-3bce-4a62-bfe8-7643757ec4f7)

</div>

### [MSD-cls Dataset](https://github.com/successhaha/GTnet)



## Ablation Study

<div align=center>

![xiaorong](https://github.com/user-attachments/assets/66e0b123-1129-411a-8a12-0776647291a3)

</div>

## Display video

Display video of AOI can be download in [Google drive](https://drive.google.com/file/d/1ULLhjB4qRHoLopkfPxRJsr2Fpq56n0c3/view?usp=drive_link).
