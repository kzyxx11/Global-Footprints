import json
import time
import requests
import folium

def fetch_coordinates(place_name):
    """
    OSINT Geocoding Engine: Resolves plaintext locations into accurate Lat/Lon coordinates
    using the OpenStreetMap Nominatim API (with polite user-agent throttling).
    """
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "GlobalFootprintBot/1.0 (asuki11_quant_nomad)"}
    params = {"q": place_name, "format": "json", "limit": 1}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200 and len(response.json()) > 0:
            data = response.json()[0]
            return float(data["lat"]), float(data["lon"])
    except Exception as e:
        print(f"[OSINT Error] Failed to resolve coordinates for {place_name}: {str(e)}")
    return None

def build_interactive_map():
    print("[Pipeline] Initializing Geodata Processing...")
    
    # Load raw location inputs
    with open("locations.json", "r") as f:
        locations = json.load(f)
        
    # Initialize global map canvas centered near Southeast Asia node
    m = folium.Map(location=[5.0, 105.0], zoom_start=5, tiles="CartoDB positron")
    
    for item in locations:
        place = item["place"]
        status = item["status"]
        desc = item["description"]
        # 📸 安全提取照片外链
        media_url = item.get("media_url", "")
        
        print(f"[Geocoding] Querying dynamic coordinates for: {place}")
        coords = fetch_coordinates(place)
        
        if coords:
            # Color matrix mapping based on digital nomad status
            marker_color = "#52b788" if status == "Base" else ("#1f77b4" if status == "Visited" else "#e63946")
            icon_style = "cloud" if status == "Base" else ("camera" if status == "Visited" else "plane")
            
            # 🖼️ 动态构建多媒体图层 (若有图片则渲染，无图片则保持纯文字，完美向下兼容)
            img_html = ""
            if media_url:
                img_html = f"""
                <div style="margin-top: 8px; width: 100%; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
                    <img src="{media_url}" style="width: 100%; height: 120px; object-fit: cover; display: block;" alt="{place}"/>
                </div>
                """
            
            # Construct customized clean HTML popup wrapper
            popup_html = f"""
            <div style="font-family: 'Arial', sans-serif; width: 220px;">
                <h4 style="margin: 0 0 5px 0; color: {marker_color}; font-size: 14px;">{place}</h4>
                <span style="font-size: 10px; background: {marker_color}; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{status.upper()}</span>
                {img_html}
                <p style="font-size: 11px; color: #555; margin: 8px 0 0 0; line-height: 1.4;">{desc}</p>
            </div>
            """
            
            # Inject beautiful dynamic nodes into canvas
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.Icon(color="white", icon_color=marker_color, icon=icon_style, prefix="fa")
            ).add_to(m)
            
            # API Courtesy Throttling (Prevents IP ban from Nominatim nodes)
            time.sleep(1.2)
            
    # Export clean autonomous front-end asset
    output_html = "index.html"
    m.save(output_html)
    print(f"[Success] Interactive geodata visualization deployed to {output_html}")

if __name__ == "__main__":
    build_interactive_map()
