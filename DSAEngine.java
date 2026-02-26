import java.util.*;
import java.io.*;

class Property {
    int id;
    String region;
    String state;
    String city;
    String type;
    int area;
    double pricePerSqFt;
    double price;
    int yearBuilt;
    double growthRate;
    int riskScore;

    public Property(String[] data) {
        this.id = Integer.parseInt(data[0]);
        this.region = data[1];
        this.state = data[2];
        this.city = data[3];
        this.type = data[4];
        this.area = Integer.parseInt(data[5]);
        this.pricePerSqFt = Double.parseDouble(data[6]);
        this.price = Double.parseDouble(data[7]);
        this.yearBuilt = Integer.parseInt(data[8]);
        this.growthRate = Double.parseDouble(data[9]);
        this.riskScore = Integer.parseInt(data[10]);
    }
}

public class DSAEngine {
    private List<Property> properties = new ArrayList<>();
    private Map<String, List<String>> adjList = new HashMap<>();

    public DSAEngine(String csvPath) {
        loadData(csvPath);
        buildCityGraph();
    }

    private void loadData(String path) {
        try (BufferedReader br = new BufferedReader(new FileReader(path))) {
            String line = br.readLine(); // skip header
            while ((line = br.readLine()) != null) {
                String[] values = line.split(",");
                properties.add(new Property(values));
            }
        } catch (IOException e) {
            System.err.println("Error loading data: " + e.getMessage());
        }
    }

    private void buildCityGraph() {
        Map<String, List<String>> stateCities = new HashMap<>();

        for (Property p : properties) {
            adjList.putIfAbsent(p.city, new ArrayList<>());
            stateCities.putIfAbsent(p.state, new ArrayList<>());
            if (!stateCities.get(p.state).contains(p.city)) {
                stateCities.get(p.state).add(p.city);
            }
        }

        // Dynamically connect cities within the same state
        for (List<String> citiesInState : stateCities.values()) {
            for (int i = 0; i < citiesInState.size(); i++) {
                String cityA = citiesInState.get(i);
                // Connect to the next 3 cities in the state to create a robust local graph
                for (int j = 1; j <= 3; j++) {
                    if (i + j < citiesInState.size()) {
                        String cityB = citiesInState.get(i + j);
                        if (!adjList.get(cityA).contains(cityB))
                            adjList.get(cityA).add(cityB);
                        if (!adjList.get(cityB).contains(cityA))
                            adjList.get(cityB).add(cityA);
                    }
                }
            }
        }
    }

    public List<String> bfsNearby(String startCity) {
        List<String> result = new ArrayList<>();
        Set<String> visited = new HashSet<>();
        Queue<String> queue = new LinkedList<>();

        queue.add(startCity);
        visited.add(startCity);

        while (!queue.isEmpty()) {
            String city = queue.poll();
            if (!city.equals(startCity))
                result.add(city);
            for (String neighbor : adjList.getOrDefault(city, new ArrayList<>())) {
                if (!visited.contains(neighbor)) {
                    visited.add(neighbor);
                    queue.add(neighbor);
                }
            }
        }
        return result;
    }

    public List<Property> searchNearby(String state, String city, String type, double targetPrice, double priceMargin) {
        List<Property> result = new ArrayList<>();

        // First find cities in the state
        List<String> validCities = new ArrayList<>();
        if (city != null && !city.trim().isEmpty() && adjList.containsKey(city)) {
            validCities.add(city);
            validCities.addAll(bfsNearby(city));
        } else {
            // If no specific city, consider all cities in state
            for (Property p : properties) {
                if (p.state.equalsIgnoreCase(state) && !validCities.contains(p.city)) {
                    validCities.add(p.city);
                }
            }
        }

        for (Property p : properties) {
            if (validCities.contains(p.city) && p.type.equalsIgnoreCase(type)) {
                if (Math.abs(p.price - targetPrice) <= priceMargin) {
                    result.add(p);
                }
            }
        }
        return result;
    }

    public List<Property> linearSearch(double budget) {
        List<Property> result = new ArrayList<>();
        for (Property p : properties) {
            if (p.price <= budget)
                result.add(p);
        }
        return result;
    }

    public void mergeSort(List<Property> props) {
        if (props.size() < 2)
            return;
        int mid = props.size() / 2;
        List<Property> left = new ArrayList<>(props.subList(0, mid));
        List<Property> right = new ArrayList<>(props.subList(mid, props.size()));

        mergeSort(left);
        mergeSort(right);

        int i = 0, j = 0, k = 0;
        while (i < left.size() && j < right.size()) {
            if (left.get(i).price <= right.get(j).price) {
                props.set(k++, left.get(i++));
            } else {
                props.set(k++, right.get(j++));
            }
        }
        while (i < left.size())
            props.set(k++, left.get(i++));
        while (j < right.size())
            props.set(k++, right.get(j++));
    }

    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("{}");
            return;
        }

        String csvPath = args[0];
        String command = args[1];
        DSAEngine engine = new DSAEngine(csvPath);

        if (command.equals("city_data")) {
            String cityName = args[2];
            System.out.println(engine.getCityDataJson(cityName));
        } else if (command.equals("multi_city_data")) {
            String[] cities = args[2].split(",");
            StringBuilder out = new StringBuilder("{");
            for (int i = 0; i < cities.length; i++) {
                String city = cities[i].trim();
                out.append("\"").append(city).append("\":").append(engine.getCityDataJson(city));
                if (i < cities.length - 1)
                    out.append(",");
            }
            out.append("}");
            System.out.println(out.toString());
        } else if (command.equals("filter")) {
            double budget = Double.parseDouble(args[2]);
            List<Property> filtered = engine.linearSearch(budget);
            System.out.println(formatProperties(filtered));
        } else if (command.equals("sort")) {
            List<Property> sorted = new ArrayList<>(engine.properties);
            engine.mergeSort(sorted);
            if (args.length > 2 && args[2].equals("desc")) {
                Collections.reverse(sorted);
            }
            System.out.println(formatProperties(sorted));
        } else if (command.equals("search")) {
            double target = Double.parseDouble(args[2]);
            // Simplified binary search for CLI
            List<Property> sorted = new ArrayList<>(engine.properties);
            engine.mergeSort(sorted);
            Property found = engine.binarySearchInternal(sorted, target);
            if (found != null) {
                System.out.println(formatProperty(found));
            } else {
                System.out.println("{}");
            }
        } else if (command.equals("search_nearby")) {
            if (args.length < 5) {
                System.out.println("[]");
                return;
            }
            String state = args[2];
            String city = args[3];
            String type = args[4];
            double targetPrice = args.length > 5 ? Double.parseDouble(args[5]) : 0;
            double margin = args.length > 6 ? Double.parseDouble(args[6]) : targetPrice * 0.2; // 20% margin default
            List<Property> nearby = engine.searchNearby(state, city, type, targetPrice, margin);
            System.out.println(formatProperties(nearby));
        }
    }

    private String getCityDataJson(String cityName) {
        List<Property> cityProps = new ArrayList<>();
        for (Property p : properties) {
            if (p.city.equalsIgnoreCase(cityName))
                cityProps.add(p);
        }
        if (cityProps.isEmpty())
            return "{}";

        double total = 0;
        Map<String, Integer> typeCount = new HashMap<>();
        Map<String, Double> typePriceSum = new HashMap<>();
        Map<String, Integer> typePriceCount = new HashMap<>();

        for (Property p : cityProps) {
            total += p.price;
            typeCount.put(p.type, typeCount.getOrDefault(p.type, 0) + 1);
            typePriceSum.put(p.type, typePriceSum.getOrDefault(p.type, 0.0) + p.pricePerSqFt);
            typePriceCount.put(p.type, typePriceCount.getOrDefault(p.type, 0) + 1);
        }

        StringBuilder out = new StringBuilder("{");
        out.append("\"name\":\"").append(cityName).append("\",");
        out.append("\"state\":\"").append(cityProps.get(0).state).append("\",");
        out.append("\"avg_price\":").append(total / cityProps.size()).append(",");
        out.append("\"count\":").append(cityProps.size()).append(",");
        out.append("\"nearby\":").append(formatList(bfsNearby(cityName))).append(",");
        out.append("\"type_distribution\":").append(formatMap(typeCount)).append(",");

        Map<String, Double> typeAvgPrices = new HashMap<>();
        for (String type : typePriceSum.keySet()) {
            typeAvgPrices.put(type, typePriceSum.get(type) / typePriceCount.get(type));
        }
        out.append("\"type_avg_prices\":").append(formatDoubleMap(typeAvgPrices));
        out.append("}");
        return out.toString();
    }

    private Property binarySearchInternal(List<Property> sorted, double target) {
        int low = 0, high = sorted.size() - 1;
        while (low <= high) {
            int mid = (low + high) / 2;
            double price = sorted.get(mid).price;
            if (Math.abs(price - target) < 1000)
                return sorted.get(mid);
            if (price < target)
                low = mid + 1;
            else
                high = mid - 1;
        }
        return null;
    }

    private static String formatProperties(List<Property> props) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < props.size(); i++) {
            sb.append(formatProperty(props.get(i)));
            if (i < props.size() - 1)
                sb.append(",");
            if (i > 100) { // Limit output for CLI performance
                sb.append("]");
                return sb.toString().replace(",]", "]");
            }
        }
        return sb.append("]").toString();
    }

    private static String formatProperty(Property p) {
        return String.format(
                "{\"Property_ID\":%d,\"City\":\"%s\",\"Property_Type\":\"%s\",\"Area_SqFt\":%d,\"Price_Per_SqFt\":%.2f,\"Current_Price\":%.2f}",
                p.id, p.city, p.type, p.area, p.pricePerSqFt, p.price);
    }

    private static String formatList(List<String> list) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < list.size(); i++) {
            sb.append("\"").append(list.get(i)).append("\"");
            if (i < list.size() - 1)
                sb.append(",");
        }
        return sb.append("]").toString();
    }

    private static String formatMap(Map<String, Integer> map) {
        StringBuilder sb = new StringBuilder("{");
        int i = 0;
        for (Map.Entry<String, Integer> entry : map.entrySet()) {
            sb.append("\"").append(entry.getKey()).append("\":").append(entry.getValue());
            if (i++ < map.size() - 1)
                sb.append(",");
        }
        return sb.append("}").toString();
    }

    private static String formatDoubleMap(Map<String, Double> map) {
        StringBuilder sb = new StringBuilder("{");
        int i = 0;
        for (Map.Entry<String, Double> entry : map.entrySet()) {
            sb.append("\"").append(entry.getKey()).append("\":").append(entry.getValue());
            if (i++ < map.size() - 1)
                sb.append(",");
        }
        return sb.append("}").toString();
    }
}
