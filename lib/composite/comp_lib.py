from __future__ import print_function
import numpy, Nio, Ngl, os, sys
from wrf import getvar, get_pyngl, smooth2d, latlon_coords, to_np

# function to retrieve the sea level pressure from the input data
def get_sea_level_pressure(wrf_data):
  slp = getvar(wrf_data,"slp")                    # sea level pressure (2D)
  slp = smooth2d(slp, 3)                          # Smooth sea level pressure
  return slp

# function to retrieve the latitude wind component from the input data
def get_latitude_wind(wrf_data):
  u10 = getvar(wrf_data,"U10")                    # Get 10m u component
  u10 = u10 * 1.94386                             # Convert to knots
  return u10

# function to retrieve the longitude wind component from the input data
def get_longitude_wind(wrf_data):
  v10 = getvar(wrf_data,"V10")                    # Get 10m v component
  v10 = v10 * 1.94386                             # Convert to knots
  return v10

# function to generate the output image for the given timestep
def print_comp_for_timestamp(wrf_data):
  slp = get_sea_level_pressure(wrf_data)
  temperature = getvar(wrf_data,"tc")
  u = get_latitude_wind(wrf_data)
  v = get_longitude_wind(wrf_data)

  lat, lon = latlon_coords(temperature)
  lat_normal = to_np(lat)
  lon_normal = to_np(lon)
  
  # temperature
  t_res = get_pyngl(temperature)
  t_res.tfDoNDCOverlay      = True                   # required for native projection
  t_res.nglDraw             = False                  # don't draw plot
  t_res.nglFrame            = False                  # don't advance frame
  t_res.cnFillOn            = True                   # turn on contour fill
  t_res.cnLinesOn           = False                  # turn off contour lines
  t_res.cnLineLabelsOn      = False                  # turn off line labels
  t_res.cnFillMode          = "RasterFill"           # These two resources
  t_res.trGridType          = "TriangularMesh"       # can speed up plotting.
  t_res.cnFillPalette       = "ncl_default"
  t_res.mpGeophysicalLineColor = "black"
  t_res.mpGeophysicalLineThicknessF = 5
  t_res.mpNationalLineColor = "gray75"
  t_res.mpNationalLineThicknessF = 5
  t_res.mpDataBaseVersion   = "MediumRes"
  
  t_res.lbOrientation       = "horizontal"
  t_res.pmLabelBarHeightF   = 0.08
  t_res.pmLabelBarWidthF    = 0.65
  t_res.lbTitleString       = "%s (%s)" % (temperature.description,temperature.units)
  t_res.lbTitleFontHeightF  = 0.015
  t_res.lbLabelFontHeightF  = 0.015                  
  #opts_T.cnFillPalette     = "BlAqGrYeOrReVi200"


  # pressure
  p_res = Ngl.Resources()
  p_res.nglDraw             =  False                 # don't draw plot
  p_res.nglFrame            =  False                 # don't advance frame
  p_res.cnHighLabelsOn      = True                   # Set labels
  p_res.cnLowLabelsOn       = True
  p_res.cnLineThicknessF    = 2
  p_res.cnMonoLineColor     = True                     
  p_res.cnLineColor         = "gray50"
  p_res.cnLineLabelInterval = 4
  p_res.sfXArray            =  lon_normal
  p_res.sfYArray            =  lat_normal
  
  # wind
  uv_res = Ngl.Resources()
  uv_res.nglDraw            =  False                # don't draw plot
  uv_res.nglFrame           =  False                # don't advance frame
  uv_res.vcFillArrowsOn     = True
  uv_res.vcRefMagnitudeF    = 30.0
  uv_res.vcRefLengthF       = 0.02
  uv_res.vcMinDistanceF     = 0.02
  uv_res.vcRefAnnoFontHeightF = 0.005
  uv_res.vfXArray           =  lon_normal
  uv_res.vfYArray           =  lat_normal

  wk_res = Ngl.Resources()
  wk_res.wkWidth = 2500
  wk_res.wkHeight = 2500
  wks_comp = Ngl.open_wks("png","comp_test", wk_res)

  # creating plots for the measurands
  tplot = Ngl.contour_map(wks_comp,temperature[0,:,:],t_res)
  pplot = Ngl.contour(wks_comp,slp,p_res)
  vector = Ngl.vector(wks_comp,u,v,uv_res)
  
  Ngl.overlay(tplot, pplot)
  Ngl.overlay(tplot, vector)
  Ngl.maximize_plot(wks_comp, tplot)
  Ngl.draw(tplot)
  Ngl.frame(wks_comp)
  Ngl.end()