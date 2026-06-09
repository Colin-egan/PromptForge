"""
Print-Readiness Analyzer for 3D Models

This module provides geometric analysis for 3D models to detect printability issues
including wall thickness, overhangs, trapped volumes, manifold validation, and
dimensional checks.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False
    logger.warning("trimesh not available - geometric analysis will be limited")


@dataclass
class AnalysisIssue:
    """Represents a single printability issue"""
    severity: str  # "critical", "warning", "info"
    category: str  # "wall_thickness", "overhang", "trapped_volume", "manifold", "dimensions"
    message: str
    details: Dict[str, Any]
    suggestion: str


@dataclass
class AnalysisResult:
    """Complete analysis result for a 3D model"""
    status: str  # "ready", "needs_attention", "not_printable"
    issues: List[AnalysisIssue]
    metadata: Dict[str, Any]
    recommendations: List[str]


class GeometricAnalyzer:
    """Analyzes 3D models for print-readiness"""
    
    # Thresholds for FDM printing (in mm)
    MIN_WALL_THICKNESS_FDM = 0.8
    MIN_WALL_THICKNESS_RESIN = 0.4
    MIN_FEATURE_SIZE = 0.5
    MAX_OVERHANG_ANGLE = 45.0  # degrees from vertical
    
    # Common print bed sizes (in mm)
    COMMON_PRINT_BEDS = {
        "small": (150, 150, 150),    # Prusa Mini
        "medium": (220, 220, 250),   # Prusa i3 MK3S, Ender 3
        "large": (300, 300, 400),    # CR-10, Ender 5 Plus
    }
    
    def __init__(self, print_technology: str = "fdm"):
        """
        Initialize analyzer
        
        Args:
            print_technology: "fdm" or "resin"
        """
        self.print_technology = print_technology.lower()
        self.min_wall_thickness = (
            self.MIN_WALL_THICKNESS_FDM if self.print_technology == "fdm"
            else self.MIN_WALL_THICKNESS_RESIN
        )
        
        if not TRIMESH_AVAILABLE:
            logger.warning("trimesh not available - analysis will be limited")
    
    def analyze_model(self, stl_path: Path) -> AnalysisResult:
        """
        Perform complete analysis on a 3D model
        
        Args:
            stl_path: Path to STL file
            
        Returns:
            AnalysisResult with all findings
        """
        if not TRIMESH_AVAILABLE:
            return self._create_limited_result()
        
        try:
            # Load mesh
            mesh = trimesh.load(str(stl_path))
            
            if not isinstance(mesh, trimesh.Trimesh):
                # Handle scene or other types
                if isinstance(mesh, trimesh.Scene):
                    mesh = mesh.dump(concatenate=True)
                else:
                    raise ValueError(f"Unexpected mesh type: {type(mesh)}")
            
            issues = []
            
            # Run all analysis checks
            issues.extend(self._check_manifold(mesh))
            issues.extend(self._check_dimensions(mesh))
            issues.extend(self._check_overhangs(mesh))
            issues.extend(self._check_wall_thickness(mesh))
            issues.extend(self._check_trapped_volumes(mesh))
            
            # Extract metadata
            metadata = self._extract_metadata(mesh)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(issues, metadata)
            
            # Determine overall status
            status = self._determine_status(issues)
            
            return AnalysisResult(
                status=status,
                issues=issues,
                metadata=metadata,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error analyzing model: {e}", exc_info=True)
            return AnalysisResult(
                status="error",
                issues=[AnalysisIssue(
                    severity="critical",
                    category="error",
                    message=f"Failed to analyze model: {str(e)}",
                    details={},
                    suggestion="Check that the STL file is valid and not corrupted"
                )],
                metadata={},
                recommendations=[]
            )
    
    def _check_manifold(self, mesh: 'trimesh.Trimesh') -> List[AnalysisIssue]:
        """Check if mesh is manifold (watertight)"""
        issues = []
        
        if not mesh.is_watertight:
            issues.append(AnalysisIssue(
                severity="critical",
                category="manifold",
                message="Model is not watertight (non-manifold geometry)",
                details={
                    "is_watertight": False,
                    "euler_number": mesh.euler_number
                },
                suggestion="Repair the mesh using mesh repair tools or regenerate the model"
            ))
        
        # Check for self-intersections
        if mesh.is_watertight and not mesh.is_volume:
            issues.append(AnalysisIssue(
                severity="warning",
                category="manifold",
                message="Model may have self-intersections",
                details={"is_volume": False},
                suggestion="Check for overlapping geometry and fix intersections"
            ))
        
        return issues
    
    def _check_dimensions(self, mesh: 'trimesh.Trimesh') -> List[AnalysisIssue]:
        """Check model dimensions and feature sizes"""
        issues = []
        bounds = mesh.bounds
        dimensions = bounds[1] - bounds[0]
        
        # Check if model fits common print beds
        fits_small = all(d <= s for d, s in zip(dimensions, self.COMMON_PRINT_BEDS["small"]))
        fits_medium = all(d <= s for d, s in zip(dimensions, self.COMMON_PRINT_BEDS["medium"]))
        fits_large = all(d <= s for d, s in zip(dimensions, self.COMMON_PRINT_BEDS["large"]))
        
        if not fits_small and not fits_medium and not fits_large:
            issues.append(AnalysisIssue(
                severity="critical",
                category="dimensions",
                message=f"Model is too large for common print beds ({dimensions[0]:.1f} x {dimensions[1]:.1f} x {dimensions[2]:.1f} mm)",
                details={
                    "dimensions": dimensions.tolist(),
                    "fits_small": False,
                    "fits_medium": False,
                    "fits_large": False
                },
                suggestion="Scale down the model or split it into multiple parts"
            ))
        elif not fits_small and not fits_medium:
            issues.append(AnalysisIssue(
                severity="info",
                category="dimensions",
                message=f"Model requires a large print bed ({dimensions[0]:.1f} x {dimensions[1]:.1f} x {dimensions[2]:.1f} mm)",
                details={
                    "dimensions": dimensions.tolist(),
                    "fits_large": True
                },
                suggestion="Ensure your printer has at least 300x300x400mm build volume"
            ))
        
        # Check for very small features
        min_dimension = min(dimensions)
        if min_dimension < self.MIN_FEATURE_SIZE:
            issues.append(AnalysisIssue(
                severity="warning",
                category="dimensions",
                message=f"Model has very small features (minimum dimension: {min_dimension:.2f}mm)",
                details={"min_dimension": float(min_dimension)},
                suggestion="Small features may not print reliably. Consider scaling up or simplifying."
            ))
        
        # Check aspect ratio for stability
        max_dimension = max(dimensions)
        aspect_ratio = max_dimension / min_dimension
        if aspect_ratio > 10:
            issues.append(AnalysisIssue(
                severity="warning",
                category="dimensions",
                message=f"Model has extreme aspect ratio ({aspect_ratio:.1f}:1)",
                details={"aspect_ratio": float(aspect_ratio)},
                suggestion="Tall/thin models may be unstable. Consider adding a base or supports."
            ))
        
        return issues
    
    def _check_overhangs(self, mesh: 'trimesh.Trimesh') -> List[AnalysisIssue]:
        """Detect overhangs that require supports"""
        issues = []
        
        try:
            # Calculate face normals
            face_normals = mesh.face_normals
            
            # Z-component of normals (pointing down means overhang)
            z_components = face_normals[:, 2]
            
            # Angle from vertical (0 = horizontal, 90 = vertical)
            angles = np.degrees(np.arccos(np.abs(z_components)))
            
            # Find overhangs (angles > threshold)
            overhang_threshold = 90 - self.MAX_OVERHANG_ANGLE
            overhang_faces = angles > overhang_threshold
            
            if np.any(overhang_faces):
                num_overhangs = np.sum(overhang_faces)
                max_angle = np.max(angles[overhang_faces])
                
                severity = "warning" if max_angle < 60 else "critical"
                
                issues.append(AnalysisIssue(
                    severity=severity,
                    category="overhang",
                    message=f"Model has {num_overhangs} faces with overhangs requiring supports",
                    details={
                        "num_overhang_faces": int(num_overhangs),
                        "max_overhang_angle": float(max_angle),
                        "threshold_angle": float(overhang_threshold)
                    },
                    suggestion=f"Add supports for overhangs steeper than {self.MAX_OVERHANG_ANGLE}° or reorient the model"
                ))
        
        except Exception as e:
            logger.warning(f"Error checking overhangs: {e}")
        
        return issues
    
    def _check_wall_thickness(self, mesh: 'trimesh.Trimesh') -> List[AnalysisIssue]:
        """Check for thin walls using ray casting"""
        issues = []
        
        try:
            # Sample points on the mesh surface
            points, face_indices = trimesh.sample.sample_surface(mesh, count=1000)
            
            # Get normals at sample points
            normals = mesh.face_normals[face_indices]
            
            # Cast rays inward to measure wall thickness
            ray_origins = points + normals * 0.01  # Offset slightly
            ray_directions = -normals
            
            # Find intersections
            locations, index_ray, index_tri = mesh.ray.intersects_location(
                ray_origins=ray_origins,
                ray_directions=ray_directions,
                multiple_hits=False
            )
            
            if len(locations) > 0:
                # Calculate distances
                distances = np.linalg.norm(locations - ray_origins[index_ray], axis=1)
                
                # Find thin walls
                thin_walls = distances < self.min_wall_thickness
                
                if np.any(thin_walls):
                    min_thickness = np.min(distances[thin_walls])
                    num_thin = np.sum(thin_walls)
                    
                    issues.append(AnalysisIssue(
                        severity="warning",
                        category="wall_thickness",
                        message=f"Model has thin walls (minimum: {min_thickness:.2f}mm, recommended: {self.min_wall_thickness}mm)",
                        details={
                            "min_thickness": float(min_thickness),
                            "recommended_thickness": self.min_wall_thickness,
                            "num_thin_areas": int(num_thin),
                            "print_technology": self.print_technology
                        },
                        suggestion=f"Increase wall thickness to at least {self.min_wall_thickness}mm for reliable printing"
                    ))
        
        except Exception as e:
            logger.warning(f"Error checking wall thickness: {e}")
        
        return issues
    
    def _check_trapped_volumes(self, mesh: 'trimesh.Trimesh') -> List[AnalysisIssue]:
        """Check for trapped volumes (enclosed cavities)"""
        issues = []
        
        try:
            # Split mesh into connected components
            components = mesh.split(only_watertight=False)
            
            if len(components) > 1:
                # Check if any components are fully enclosed
                for i, component in enumerate(components):
                    if isinstance(component, trimesh.Trimesh) and component.is_watertight:
                        # Check if this component is inside another
                        # (simplified check - could be more sophisticated)
                        if i > 0:  # Assume first component is outer shell
                            issues.append(AnalysisIssue(
                                severity="warning",
                                category="trapped_volume",
                                message="Model may have enclosed cavities that could trap resin or support material",
                                details={"num_components": len(components)},
                                suggestion="Add drainage holes or remove internal geometry"
                            ))
                            break
        
        except Exception as e:
            logger.warning(f"Error checking trapped volumes: {e}")
        
        return issues
    
    def _extract_metadata(self, mesh: 'trimesh.Trimesh') -> Dict[str, Any]:
        """Extract useful metadata from mesh"""
        bounds = mesh.bounds
        dimensions = bounds[1] - bounds[0]
        
        return {
            "volume": float(mesh.volume),
            "surface_area": float(mesh.area),
            "dimensions": {
                "x": float(dimensions[0]),
                "y": float(dimensions[1]),
                "z": float(dimensions[2])
            },
            "bounding_box": {
                "min": bounds[0].tolist(),
                "max": bounds[1].tolist()
            },
            "num_faces": int(len(mesh.faces)),
            "num_vertices": int(len(mesh.vertices)),
            "is_watertight": bool(mesh.is_watertight),
            "center_mass": mesh.center_mass.tolist()
        }
    
    def _generate_recommendations(self, issues: List[AnalysisIssue], metadata: Dict[str, Any]) -> List[str]:
        """Generate print recommendations based on analysis"""
        recommendations = []
        
        # Orientation recommendation
        dims = metadata["dimensions"]
        if dims["z"] > dims["x"] and dims["z"] > dims["y"]:
            recommendations.append("Print upright (as oriented) for best strength")
        else:
            recommendations.append("Consider rotating for optimal layer adhesion")
        
        # Support recommendation
        has_overhangs = any(i.category == "overhang" for i in issues)
        if has_overhangs:
            recommendations.append("Use tree supports for overhangs to minimize material usage")
        else:
            recommendations.append("No supports needed - print as-is")
        
        # Infill recommendation
        volume = metadata["volume"]
        if volume > 100000:  # Large model
            recommendations.append("Use 15-20% infill with gyroid pattern for strength and material savings")
        else:
            recommendations.append("Use 20-25% infill for good strength-to-weight ratio")
        
        # Material recommendation
        has_thin_walls = any(i.category == "wall_thickness" for i in issues)
        if has_thin_walls:
            recommendations.append("Use PLA or PETG for easier printing of thin features")
        else:
            recommendations.append("PLA, PETG, or ABS all suitable for this model")
        
        return recommendations
    
    def _determine_status(self, issues: List[AnalysisIssue]) -> str:
        """Determine overall printability status"""
        if not issues:
            return "ready"
        
        critical_issues = [i for i in issues if i.severity == "critical"]
        if critical_issues:
            return "not_printable"
        
        warning_issues = [i for i in issues if i.severity == "warning"]
        if warning_issues:
            return "needs_attention"
        
        return "ready"
    
    def _create_limited_result(self) -> AnalysisResult:
        """Create a limited result when trimesh is not available"""
        return AnalysisResult(
            status="ready",
            issues=[AnalysisIssue(
                severity="info",
                category="error",
                message="Geometric analysis not available (trimesh library not installed)",
                details={},
                suggestion="Install trimesh for detailed print-readiness analysis"
            )],
            metadata={},
            recommendations=["Basic model validation only - install trimesh for full analysis"]
        )


def analyze_stl(stl_path: Path, print_technology: str = "fdm") -> AnalysisResult:
    """
    Convenience function to analyze an STL file
    
    Args:
        stl_path: Path to STL file
        print_technology: "fdm" or "resin"
        
    Returns:
        AnalysisResult
    """
    analyzer = GeometricAnalyzer(print_technology=print_technology)
    return analyzer.analyze_model(stl_path)

# Made with Bob
