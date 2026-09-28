float2 p = World.xy;
float2 flow = float2(.819152, .573576);
float a = dot(p,flow)-Seconds*7.0;
float b = dot(p,float2(-flow.y,flow.x));
float phase = b*.088+sin(a*.014)*.7+sin(a*.031)*.24;
float fade = 1-saturate(length(float2(ddx(phase),ddy(phase)))*.55);
float slope = cos(phase)*.035*fade;
return normalize(SurfaceNormal + float3(-flow.y*slope,flow.x*slope,0)*saturate(SurfaceNormal.z));
