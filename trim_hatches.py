import rhinoscriptsyntax as rs
import operator

hatch = rs.GetObject(message="Pick any hatch", filter=rs.filter.hatch)
trim_lines = rs.GetObjects(message="Select cutting lines", filter=rs.filter.curve)

# Project trim_lines to cplane
plane = rs.ViewCPlane()
matrix = rs.XformPlanarProjection(plane)
rs.TransformObjects(trim_lines, matrix, copy=False)

selected_objects = []
selected_objects.append(trim_lines)

if hatch:
    # Store original hatch settings
    hatch_pattern = rs.HatchPattern(hatch)
    hatch_rotation = rs.HatchRotation(hatch)
    hatch_scale = rs.HatchScale(hatch)
    
    # Make hatch solid so we able to explode it and get surface instead
    if hatch_pattern != "Solid":
        rs.HatchPattern(hatch, "Solid")
    dup_border_surface = []
    dup_border_surface.append(rs.ExplodeHatch(hatch)[0])
    rs.SurfaceIsocurveDensity(dup_border_surface, 100)
    selected_objects.append(dup_border_surface)
    reduced_selected_objects = reduce(operator.add, selected_objects)
    rs.SelectObjects(reduced_selected_objects)
    rs.HideObject(hatch)
    rs.Command("_Trim")
    trimmed_surface = rs.LastCreatedObjects()
    
    new_borders = []
    if trimmed_surface:
        for surface in trimmed_surface:
            new_borders.append(rs.DuplicateSurfaceBorder(surface))
            selected_objects.append(new_borders)
        # Keep trimming lines but everything else will be deleted further
        selected_objects.remove(trim_lines)
        new_hatches = rs.AddHatches(new_borders, hatch_pattern, hatch_scale, hatch_rotation)
        rs.MatchObjectAttributes(new_hatches, hatch)
        rs.ShowObject(new_hatches)
       rs.DeleteObjects(trimmed_surface)
    else:
        print("No trimmed surfaces was created.")
else:
    print("No hatches was selected.")
