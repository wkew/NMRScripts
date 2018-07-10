# Background
In 2017, we published a paper ([open access](https://onlinelibrary.wiley.com/doi/abs/10.1002/mrc.4621)) detailing a new method for automated solvent suppression of ethanol and water in Scotch Whisky (applicable to all alcoholic spirits) for <sup>1</sup>H NMR. 
This method was developed on Bruker Avance III HD console equipped high field (600, 800 MHz) spectrometers equipped with TCI cryoprobes and three channels (plus deuterium for lock). 
The basic experiment involved application of a CW presaturation pulse on water on channel 3, decoupling during presaturation of the <sup>13</sup>C carbons of ethanol on channel 2, and presaturation of the ethanol CH<sub>2</sub> and CH<sub>3</sub> signals. These were coupled with the well known 1D NOESY presaturation sequence commonly used in metabolomics studies. 

What was a challenge, though, was to develop a means to optimise this per-sample. Given the variable ethanol strength, pH, and composition of different samples, it was inevitable that chemical shifts (and signal intensities to suppress) would vary across samples. As such, a four-part composite experiment was developed to determine the correct frequencies to suppress and to create the necessary shaped pulses and calculate the power levels and pulse lengths. A number of TopSpin AU and Python scripts were developed to automate these calculations. The purpose of this blog post is to overview (and provide) these scripts and provide practical implementation tips to other groups.

# Overview
The composite experiments have four parts. Because of the scripted nature of the automation, by default the experiments must be run in the correct order with the correct experiment numbers (expno).

**Expno 10** is the first experiment. The parameter set should be read in, and the AU acquisition program run. This executes getprosol, performs pulse calibrations (channel F1 and F3), finds the resonance frequency of water, and finally acquires a simple zgpr spectrum with water OH (but not ethanol CH2/CH3) suppressed. This spectrum provides a quick QC check that the sampled shimmed OK. (Shimming concentrated ethanol/water solutions has proven to be tricky on occasion in our experience.) It creates additional expno folders (99999, 99998, 99997) to store pulsecal parameters. The associated AU program is efindwater2.wk, available on GitHub. For high strength samples (ethanol > 50%) the linear backprediction of only 512 points is necessary - 4096 is too many any entirely removes the OH signal - and an additional au program is provided, efindwater2-highABV.wk.

**Expno 11** is the second experiment. Again, the parameter set should be read in, and the AU automation program executed. Note for this (and the remaining experiments) all the AU program does is execute a Python script which performs the necessary steps. This experiment acquires a reverse INEPT spectrum fo the ethanol CH2/CH3 signals. The Python script phases the spectrum and peak picks (within narrow ranges to avoid the residual C-12 isotopomer signals) the C-13 signals, calculating the mid-point of each of the quartet and triplet, and their distance apart. This allows determination of the frequency to 'sit' on resonance on F1 in the final experiment, and the offset frequency to simultaneously suppress. The script calculates the necessary shaped pulse, called "EthanolShape". This AU script is called createEthanolShape, and the Python script it calls is createEthanolShape_wk.py. 

**Expno 12** is the third experiment. It acquires a simple zgig 13C spectrum in one scan. The AU program ( [createCarbonShape](./au/createCarbonShape) ) calls the Python script (createCarbonShape.py) which again processes and peak picks the spectrum, detemrining the exact frequencies of the 13C signals of ethanol, and their midpoint. The decoupling pulse in the final experiment is applied simultaneously at both frequencies, whilst the channel is set to the midpoint frequency between them. Again, frequency ranges are defined for peak picking, although only two signals should be observed in the experiment as described. If samples had high levels of acetone, methanol, or other organic solvent, there may be additional peaks which should not be picked. The calculated pulse lengths and shape (CarbonShape) is stored.

**Expno 13** is the final experiment, which acquires the solvent suppressed spectrum. AU program (acqWhiskey) calls Python script (acqWhiskey.py), reads from each of the previous experiment numbers the calculated pulse lengths, power levels, and shapes, and starts the acquisition. It performs a couple of quick power level checks to protect against damage to the hardware - if the wrong peaks have been picked, the power levels may be wildly off and far too high. Acquisition will not start if the power level is too high. 

# Side notes
Calculation of shaped pulses can be highly precise, however the spectrometer hardware has timing limitations. Specifically, every pulse element must last at least 25 nanoseconds or a multiple of this. A shaped pulse of 1000 points lasting 1 ms therefore contains 1000 x 1 us elements, which is acceptable. If it lasted 1.01 ms, each point would last 1.01 us, which is not an exact multiple of 25 ns. A FIFO error would result as the SGU cannot perform the task, and acquisition would fail. Therefore, the Python scripts adjust the calculated exact shaped pulse lengths and number of points in each shape to ensure the pulses are suitable. For the EthanolShape, 1000 points are used and the pulse is sufficiently long (appox 50 ms) that simple means can be used to round it (calculated pulse length divised by number of points and minimum length, converted to integer, and multipled by back by number of points and minimum length.) For CarbonShape, fewer points are necessary, but the pulse is much shorter (2.5 ms), so it is 'harder' to achieve a close and accurate rounding. Thus, the number of points are varied between 475 and 525 as well as exact pulse length to fit the criteria.

# Scripts
The scripts are available on GitHub. See here - [https://github.com/wkew/NMRScripts/ ](https://github.com/wkew/NMRScripts/)

They were originally written by Boris Mitrovich, with modifications by myself. They are free, open source, GPL v3. 
Standard Bruker locations for storage are (for TopSpin3.5 on Windows):

`C:\Bruker\TopSpin3.5\exp\stan\nmr\au\src\user`

`C:\Bruker\TopSpin3.5\exp\stan\nmr\py\user`

Equivalent directories for other versions of TopSpin, and for Linux installations (e.g. `/opt/TopSpin3.5/exp/`....)

Acquired datasets are available here - [https://datashare.is.ed.ac.uk/handle/10283/2733](https://datashare.is.ed.ac.uk/handle/10283/2733) (and can be basis for parameter sets). 
