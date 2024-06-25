$(document).ready(function() {
    $.getJSON('something.json', function(data) {
        if (data.length === 0) {
            console.error("No data found in JSON file.");
        } else {
            console.log("Data loaded:", data);
        }

        // Display the last updated timestamp
        $('#lastUpdated').text('Last updated: ' + data.last_updated);

        $.fn.dataTable.ext.errMode = 'none';
        var table = $('#jobTable').DataTable({
                ajax: {
                    url: 'something.json',
                    dataSrc: function(json) {
                        return json.data;
                    },
                    error: function(xhr, status, error) {
                        console.error("Failed to load JSON file:", status, error);
                        $('#jobTable').html('<p class="text-danger">Failed to load data. Please try again later.</p>');
                    }
                },
            order: [[0, 'desc']],
            columns: [
                { data: 'unique_id' },
                { data: 'Etablissement organisateur',
                render: function ( data, type, row ) {
                    return '<span style="white-space:normal">' + data + "</span>";
                }},
                { data: 'Grade', render: function(data, type, row) {
                    if (data.link) {
                        return '<a href="' + data.link + '"><span style="white-space:normal">' + data.text + '</span></a>';
                    }
                    return data;
                }},
                {data: 'Nombre postes',
                render: function ( data, type, row ) {
                    return '<span style="white-space:normal">' + data + "</span>";
                }},
                { data: 'Délai dépôt' },
                { data: 'Date concours' },
                { data: 'Date publication' },
                { data: "Candidats convoqués pour l'examen écrit" },
                { data: "Candidats convoqués pour l'entretien oral" },
                { data: 'Résultats' },
                { data: 'Désistements' }
            ],
            dom: 'Bfrtip',
            responsive: {
                details: {
                    display: $.fn.dataTable.Responsive.display.modal({
                        header: function(row) {
                            var data = row.data();
                            return 'Details for ' + data[1] + ' ' + data[2]+' ';
                        }
                    }),
                    renderer: $.fn.dataTable.Responsive.renderer.tableAll({
                        tableClass: 'table'
                    })
                }
            },
            responsive: true,
        autoWidth: true,
        scrollX: true,  // Enable horizontal scrolling
        processing: true,
        searchPanes: {
            collapse: true,
            clear: false,
            initCollapsed: false,
            cascadePanes: true,
            layout: 'columns-1',
            dtOpts: {
                dom: 'tp',
                paging: 'true',
                pagingType: 'simple',
                searching: 'true'
            },
            columns: [1]
            },
            lengthMenu: [
                [10, 25, 50, 100, -1],
                ['10 lignes', '25 lignes', '50 lignes', '100 lignes', 'Afficher tous']
            ],
            "dom": "P" +
                "<'row'<'col-sm-6 col-md-4'l><'col-sm-6 col-md-3'B><'col-sm-12 col-md-5'f>>" +
                "<'row'<'col-sm-12'tr>>" +
                "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
            "buttons": {
                dom: {
                    button: {
                        tag: 'button',
                        className: ''
                    }
                },
                "buttons": [{
                        extend: 'excelHtml5',
                        text: '<i class="fas fa-file-excel"></i>',
                        titleAttr: "Exporter Excel",
                        className: 'btn btn-success',
                    },
                    {
                        extend: 'csvHtml5',
                        text: '<i class="fas fa-file-csv"></i>',
                        titleAttr: "Exporter PDF",
                        className: 'btn btn-danger'
                    },

                    {
                        extend: 'print',
                        text: '<i class="fas fa-print"></i>',
                        titleAttr: "Imprimer",
                        className: 'btn btn-info'
                    }
                ]
            },
            "pageLength": 50,
            order: [[0, 'desc']]
        });

        // Apply the search
        $('#searchEtablissement').on('keyup', function() {
            table.column(1).search(this.value).draw();
        });

        $('#searchGrade').on('keyup', function() {
            table.column(2).search(this.value).draw();
        });
    }).fail(function() {
        console.error("Failed to load JSON file.");
    });
});