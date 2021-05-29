function fillEditProductModal(obj) {
        var product_row = document.getElementById('row-'+obj.id).cells
        document.getElementById('editfloatingid').value = product_row[0].innerHTML;
        document.getElementById('editfloatingid').readOnly = true;
        document.getElementById('editfloatingName').value = product_row[1].innerHTML;
        document.getElementById('editfloatingAbout').value = product_row[2].getAttribute('data-target');
        document.getElementById('editfloatingImage').value = product_row[3].innerHTML;
        document.getElementById('editfloatingStock').value = product_row[4].innerHTML;
        document.getElementById('editfloatingCost').value = product_row[5].innerHTML;
        document.getElementById('editselectCategory').selectedIndex = product_row[6].innerHTML.split('-')[0];
    }

function fillEditCategoryModal(obj) {
    var category_row = document.getElementById('category-row-'+obj.id).cells
    document.getElementById('edit_id_category').value = category_row[0].innerHTML;
    document.getElementById('edit_id_category').readOnly = true;
    document.getElementById('edit_name_category').value = category_row[1].innerHTML;
}